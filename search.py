# perfume-bot/search.py
# Обновленная логика поиска: каскадный, гибкий и устойчивый к ошибкам.

from rapidfuzz import process
from utils import normalize_for_match
from database import fetch_all_originals, fetch_clones_for_search

# Глобальные переменные для кэширования каталогов
CATALOG = []
CATALOG_BY_ID = {} # Оптимизация: для быстрого доступа к оригиналу по ID
CLONE_CATALOG = []
BRAND_MAP = {}
INITIALIZED = False

def init_catalog(conn):
    """
    Инициализирует каталоги, загружая их в память и создавая 
    вспомогательные структуры для быстрого и гибкого поиска.
    Вызывается один раз при старте бота.
    """
    global CATALOG, CLONE_CATALOG, BRAND_MAP, CATALOG_BY_ID, INITIALIZED

    # 1. Загрузка и подготовка оригиналов
    originals_data = fetch_all_originals(conn)
    temp_catalog = []
    for item in originals_data:
        brand, name = item.get("brand", ""), item.get("name", "")
        brand_norm, name_norm = normalize_for_match(brand), normalize_for_match(name)
        
        perfume_data = {
            "id": item["id"], "brand": brand, "name": name,
            "brand_norm": brand_norm, "name_norm": name_norm,
            "brand_name_norm": f"{brand_norm} {name_norm}".strip(),
            "name_brand_norm": f"{name_norm} {brand_norm}".strip(),
        }
        temp_catalog.append(perfume_data)
        CATALOG_BY_ID[item["id"]] = perfume_data
        BRAND_MAP.setdefault(brand_norm, []).append(item['id'])
    CATALOG = temp_catalog

    # 2. Загрузка и подготовка клонов
    clones_data = fetch_clones_for_search(conn)
    temp_clone_catalog = []
    for item in clones_data:
        brand, name = item.get("brand", ""), item.get("name", "")
        brand_norm, name_norm = normalize_for_match(brand), normalize_for_match(name)
        
        temp_clone_catalog.append({
            "original_id": item["original_id"],
            "brand_name_norm": f"{brand_norm} {name_norm}".strip(),
        })
    CLONE_CATALOG = temp_clone_catalog
    INITIALIZED = True

def _find_exact_match(normalized_query):
    """(Шаг 1) Ищет точное совпадение в каталоге оригиналов."""
    for item in CATALOG:
        if normalized_query == item["brand_name_norm"] or normalized_query == item["name_brand_norm"]:
            return item
    return None

def _find_original_by_clone(normalized_query):
    """(Шаг 2) Ищет клон и возвращает его оригинал."""
    choices = [item["brand_name_norm"] for item in CLONE_CATALOG]
    best_match = process.extractOne(normalized_query, choices, score_cutoff=90)
    
    if best_match:
        clone_index = choices.index(best_match[0])
        original_id = CLONE_CATALOG[clone_index]["original_id"]
        # Оптимизированный поиск по ID вместо перебора
        return CATALOG_BY_ID.get(original_id)
    return None

def _find_fuzzy_match(normalized_query):
    """(Шаг 3) Ищет лучшее нечеткое совпадение в каталоге оригиналов."""
    choices = {item["id"]: item["brand_name_norm"] for item in CATALOG}
    result = process.extractOne(normalized_query, choices, score_cutoff=85)

    if result:
        perfume_id = result[2]
        return CATALOG_BY_ID.get(perfume_id)
    return None

def _find_by_single_word(normalized_query):
    """(Шаг 4) Обрабатывает запросы из одного слова."""
    if normalized_query in BRAND_MAP and len(BRAND_MAP[normalized_query]) > 1:
        return {"type": "clarification", "message": "Кажется, вы ввели только бренд. Уточните, пожалуйста, полное название парфюма."}
    
    name_matches = [item for item in CATALOG if item["name_norm"] == normalized_query]
    if len(name_matches) == 1:
        return {"type": "found", "result": name_matches[0]}
    elif len(name_matches) > 1:
        return {"type": "clarification", "message": "Найдено несколько парфюмов с таким названием. Уточните, пожалуйста, бренд."}
    
    return None

def find_original(conn, user_text):
    """Основная функция поиска. Выполняет поиск по каскадной модели."""
    if not user_text or not user_text.strip():
        return {"ok": False, "message": "Пустой запрос. Отправьте название в формате: 'Бренд Название'."}

    if not INITIALIZED:
        init_catalog(conn)

    query_norm = normalize_for_match(user_text)
    
    # --- Каскадный поиск ---
    # Попытка 1: Точное совпадение
    if exact_match := _find_exact_match(query_norm):
        return {"ok": True, "original": exact_match, "match_type": "exact"}

    # Попытка 2: Поиск по названию клона
    if clone_match := _find_original_by_clone(query_norm):
        return {"ok": True, "original": clone_match, "match_type": "clone"}

    # Попытка 3: Обработка запроса из одного слова
    if len(query_norm.split()) == 1:
        if single_word_result := _find_by_single_word(query_norm):
            if single_word_result["type"] == "found":
                 return {"ok": True, "original": single_word_result["result"], "match_type": "fuzzy"}
            else: # "clarification"
                return {"ok": False, "message": single_word_result["message"]}

    # Попытка 4: Нечеткий (fuzzy) поиск
    if fuzzy_match := _find_fuzzy_match(query_norm):
        return {"ok": True, "original": fuzzy_match, "match_type": "fuzzy"}
    
    return {"ok": False, "message": "К сожалению, не удалось найти такой парфюм. Попробуйте проверить название и ввести его еще раз. 😅"}
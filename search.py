# perfume-bot/search.py
# Логика поиска парфюмов: гибкий поиск с приоритетом точного совпадения

from rapidfuzz import fuzz
from utils import normalize_for_match
from database import fetch_all_originals, fetch_clones_for_search, fetch_original_by_id

# Глобальные переменные каталога. Загружаются один раз при старте.
CATALOG = None
BRAND_MAP = None
NAME_MAP = None
CLONE_CATALOG = None

def _load_catalog(conn):
    """
    Загрузка всех оригиналов и клонов в память и подготовка словарей для поиска.
    Это приватная функция.
    """
    global CATALOG, BRAND_MAP, NAME_MAP, CLONE_CATALOG

    # Загрузка оригиналов
    rows = fetch_all_originals(conn)
    catalog, brand_map, name_map = [], {}, {}
    for r in rows:
        item = {
            "id": r["id"],
            "brand": r["brand"] or "",
            "name": r["name"] or "",
            "brand_norm": normalize_for_match(r["brand"]),
            "name_norm": normalize_for_match(r["name"]),
            "display_norm": normalize_for_match(f"{r['brand']} {r['name']}"),
        }
        catalog.append(item)
        brand_map.setdefault(item["brand_norm"], []).append(item)
        name_map.setdefault(item["name_norm"], []).append(item)

    # Загрузка клонов
    clone_rows = fetch_clones_for_search(conn)
    clone_catalog = []
    for r in clone_rows:
        item = {
            "brand": r["brand"] or "",
            "name": r["name"] or "",
            "display_norm": normalize_for_match(f"{r['brand']} {r['name']}"),
            "original_id": r["original_id"],
        }
        clone_catalog.append(item)

    CATALOG = catalog
    BRAND_MAP = brand_map
    NAME_MAP = name_map
    CLONE_CATALOG = clone_catalog

def init_catalog(conn):
    """Инициализация глобальных переменных каталога."""
    _load_catalog(conn)

def _find_in_catalog(user_text, search_space):
    """
    Внутренняя вспомогательная функция для поиска
    по нормализованному тексту в заданном пространстве.
    Использует fuzz.token_set_ratio для большей гибкости.
    """
    user_norm = normalize_for_match(user_text)
    
    # Сначала ищем точное совпадение
    for item in search_space:
        if item["display_norm"] == user_norm:
            return {"ok": True, "result": item, "score": 100}

    # Затем ищем fuzzy-совпадение
    best_match, score = None, 0
    for item in search_space:
        s = fuzz.token_set_ratio(user_norm, item["display_norm"])
        if s > score:
            best_match, score = item, s
    
    if best_match and score >= 90:
        return {"ok": True, "result": best_match, "score": score}
    
    return {"ok": False, "result": None, "score": 0}

def find_original(conn, user_text):
    """
    Главная функция поиска.
    """
    global CATALOG, BRAND_MAP, NAME_MAP

    if not user_text or not user_text.strip():
        return {"ok": False, "message": "Пустой запрос. Отправь в формате: 'Бренд Название'."}

    if not CATALOG:
        init_catalog(conn)

    user_norm = normalize_for_match(user_text)
    user_words = user_norm.split()

    # Проверка на наличие бренда в запросе
    found_brand = any(word in BRAND_MAP for word in user_words)
    if not found_brand and len(user_words) >= 2:
        # Если в запросе несколько слов, но нет бренда, это, скорее всего, название
        # Просто продолжаем поиск, т.к. fuzzy-поиск по display_norm это обработает.
        pass
    elif not found_brand and len(user_words) == 1:
        # Если в запросе одно слово и это не бренд, пробуем найти по названию
        for c in CATALOG:
            if fuzz.ratio(user_norm, c["name_norm"]) >= 90:
                return {"ok": True, "original": c}
        return {"ok": False, "message": "У меня не получилось найти то, что вы искали. Пожалуйста, попробуйте снова. 😅"}

    # Поиск по оригинальным парфюмам
    search_result = _find_in_catalog(user_text, CATALOG)
    if search_result["ok"]:
        return {"ok": True, "original": search_result["result"]}
    
    # Поиск по клонам
    clone_result = _find_in_catalog(user_text, CLONE_CATALOG)
    if clone_result["ok"]:
        found_clone = clone_result["result"]
        original_data = fetch_original_by_id(conn, found_clone["original_id"])
        
        if original_data:
            original_item = {
                "id": original_data["id"],
                "brand": original_data["brand"],
                "name": original_data["name"],
                "brand_norm": normalize_for_match(original_data["brand"]),
                "name_norm": normalize_for_match(original_data["name"]),
                "display_norm": normalize_for_match(f"{original_data['brand']} {original_data['name']}"),
            }
            return {"ok": True, "original": original_item}

    # Если ничего не найдено
    return {"ok": False, "message": "У меня не получилось найти то, что вы искали. Пожалуйста, попробуйте снова. 😅"}
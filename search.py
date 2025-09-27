# perfume-bot/search.py
# Логика поиска парфюмов: гибкий поиск с приоритетом точного совпадения и устойчивостью к ошибкам.

from rapidfuzz import fuzz
# Замена ratio на более устойчивый WRatio для сравнения
from rapidfuzz.fuzz import WRatio
from utils import normalize_for_match
from database import fetch_all_originals, fetch_clones_for_search, fetch_original_by_id
from i18n import get_message # <-- Import i18n

# Глобальные переменные каталога. Загружаются один раз при старте.
CATALOG = None
BRAND_MAP = None
NAME_MAP = None
CLONE_CATALOG = None

# --- Инициализация и загрузка каталога (Оставлена без изменений) ---

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

# --- Улучшенные вспомогательные функции ---

def _fuzzy_search_best(user_norm, search_space, target_key, min_score=90):
    """
    Универсальная вспомогательная функция для фаззи-поиска.
    Использует WRatio, который более устойчив к опечаткам и порядку слов.
    """
    best_match, score = None, 0
    
    # 1. Поиск точного совпадения (оптимизация)
    for item in search_space:
        if item[target_key] == user_norm:
            return {"ok": True, "result": item}

    # 2. Фаззи-поиск
    for item in search_space:
        # Используем WRatio для сравнения строк разной длины и с опечатками
        s = WRatio(user_norm, item[target_key])
        if s > score:
            best_match, score = item, s
            
    if best_match and score >= min_score:
        return {"ok": True, "result": best_match}
    
    return {"ok": False, "result": None}

def find_original_by_clone(conn, user_norm, lang="ru"): # <-- Добавлен lang
    """Ищет клон по нормализованному тексту и возвращает связанный с ним оригинал."""
    # Поиск клона в каталоге клонов
    # Минимальный скор снижен до 80, так как бренды клонов могут быть очень похожи
    search_result = _fuzzy_search_best(user_norm, CLONE_CATALOG, "display_norm", min_score=80)
    
    if search_result["ok"]:
        found_clone = search_result["result"]
        # Используем original_id для поиска оригинала в базе данных
        original_data = fetch_original_by_id(conn, found_clone["original_id"])
        
        if original_data:
            # Преобразуем данные из БД в нужный формат для возврата
            original_item = {
                "id": original_data["id"],
                "brand": original_data["brand"],
                "name": original_data["name"],
                "brand_norm": normalize_for_match(original_data["brand"]),
                "name_norm": normalize_for_match(original_data["name"]),
                "display_norm": normalize_for_match(f"{original_data['brand']} {original_data['name']}"),
            }
            return {"ok": True, "original": original_item}
    
    # Локализованное сообщение об ошибке
    return {"ok": False, "message": get_message("error_not_found", lang)}


# --- Главная функция поиска ---

def find_original(conn, user_text, lang="ru"): # <-- Добавлен lang
    """
    Главная функция поиска с многоступенчатой логикой:
    1. Проверка на пустой запрос.
    2. Инициализация каталога (если не сделано).
    3. Поиск точного совпадения "Бренд Название" (Brand Name).
    4. Поиск по клонам (если пользователь ввел название клона).
    5. Поиск по отдельным компонентам (Бренд или Название) с фаззи-логикой.
    6. Общий фаззи-поиск по "Бренд Название".
    """
    global CATALOG, BRAND_MAP, NAME_MAP

    if not user_text or not user_text.strip():
        # Локализованная ошибка
        return {"ok": False, "message": get_message("error_empty_query", lang)}

    if not CATALOG:
        init_catalog(conn)

    user_norm = normalize_for_match(user_text)
    user_words = user_norm.split()
    
    # ----------------------------------------------------
    # Шаг 1: Точное совпадение (Display Norm)
    # ----------------------------------------------------
    match = _fuzzy_search_best(user_norm, CATALOG, "display_norm", min_score=100)
    if match["ok"]:
        return {"ok": True, "original": match["result"]}

    # ----------------------------------------------------
    # Шаг 2: Поиск по клонам (пользователь мог ввести клон)
    # ----------------------------------------------------
    clone_search_result = find_original_by_clone(conn, user_norm, lang) # <-- Передача lang
    if clone_search_result["ok"]:
        return clone_search_result

    # ----------------------------------------------------
    # Шаг 3: Поиск по частям (для неполных или перепутанных запросов)
    # ----------------------------------------------------
    
    # A. Поиск по названию (Name Only) - min_score=90
    name_match = _fuzzy_search_best(user_norm, CATALOG, "name_norm", min_score=90)
    if name_match["ok"]:
        return {"ok": True, "original": name_match["result"]}

    # B. Поиск по бренду (Brand Only) - min_score=90
    brand_match = _fuzzy_search_best(user_norm, CATALOG, "brand_norm", min_score=90)
    if brand_match["ok"]:
        # Локализованное предупреждение о неполном запросе по бренду
        brand_name = brand_match['result']['brand']
        # Используем .format для подстановки названия бренда
        message = get_message("error_brand_only", lang).format(brand_name=brand_name)
        return {"ok": False, "message": message}

    # ----------------------------------------------------
    # Шаг 4: Общий Фаззи-поиск (Display Norm) - min_score=85
    # ----------------------------------------------------
    # Снижаем порог для фаззи-поиска, чтобы поймать опечатки.
    match = _fuzzy_search_best(user_norm, CATALOG, "display_norm", min_score=85)
    if match["ok"]:
        # Локализованная заметка о неточном совпадении
        note = get_message("note_fuzzy_match", lang)
        return {"ok": True, "original": match["result"], "note": note}
    
    # ----------------------------------------------------
    # Шаг 5: Неудача
    # ----------------------------------------------------
    # Локализованная ошибка "не найдено"
    return {"ok": False, "message": get_message("error_not_found", lang)}
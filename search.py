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

def _search_in_catalog(user_norm, search_space):
    """
    Внутренняя вспомогательная функция для поиска
    по нормализованному тексту в заданном пространстве.
    """
    # 1. Точное совпадение
    for item in search_space:
        if item["display_norm"] == user_norm:
            return {"ok": True, "result": item}
    
    # 2. Fuzzy-поиск
    best_match, score = None, 0
    for item in search_space:
        s = fuzz.ratio(user_norm, item["display_norm"])
        if s > score:
            best_match, score = item, s
    
    if best_match and score >= 90:
        return {"ok": True, "result": best_match}
    
    return {"ok": False, "result": None}

def find_original_by_clone(conn, clone_text):
    """Ищет клон и возвращает связанный с ним оригинал."""
    user_norm = normalize_for_match(clone_text)
    
    # Поиск клона в каталоге клонов
    search_result = _search_in_catalog(user_norm, CLONE_CATALOG)
    
    if search_result["ok"]:
        found_clone = search_result["result"]
        # Используем original_id для поиска оригинала в базе данных
        original_data = fetch_original_by_id(conn, found_clone["original_id"])
        
        if original_data:
            # Преобразуем данные из БД в нужный формат
            original_item = {
                "id": original_data["id"],
                "brand": original_data["brand"],
                "name": original_data["name"],
                "brand_norm": normalize_for_match(original_data["brand"]),
                "name_norm": normalize_for_match(original_data["name"]),
                "display_norm": normalize_for_match(f"{original_data['brand']} {original_data['name']}"),
            }
            return {"ok": True, "original": original_item}
    
    return {"ok": False, "message": "Не удалось найти оригинал для этого клона."}

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

    # Проверяем, является ли запрос одним словом
    if len(user_words) == 1:
        # Проверка на совпадение с брендом
        if user_norm in BRAND_MAP:
            return {"ok": False, "message": "Ой, простите, кажется, вы не указали название парфюма полностью. Пожалуйста, введите данные целиком, так вероятность ошибки меньше."}
        
        # Если не бренд, пробуем найти как название
        # 1. Fuzzy-поиск только по названию
        best, score = None, 0
        for c in CATALOG:
            s = fuzz.ratio(user_norm, c["name_norm"])
            if s > score:
                best, score = c, s
        if best and score >= 90:
            return {"ok": True, "original": best}
    
    # --- Стандартный поиск для запросов с несколькими словами ---
    
    # 1. Точное совпадение brand + name
    search_result = _search_in_catalog(user_norm, CATALOG)
    if search_result["ok"]:
        return {"ok": True, "original": search_result["result"]}
    
    # 2. Поиск клона и его оригинала
    clone_search_result = find_original_by_clone(conn, user_text)
    if clone_search_result["ok"]:
        return clone_search_result
    
    # 3. Fuzzy-поиск по display_norm
    best, score = None, 0
    for c in CATALOG:
        s = fuzz.ratio(user_norm, c["display_norm"])
        if s > score:
            best, score = c, s
    if best and score >= 90:
        return {"ok": True, "original": best}

    return {"ok": False, "message": "У меня не получилось найти то, что вы искали. Пожалуйста, попробуйте снова. 😅"}
# perfume-bot/search.py
# Логика поиска парфюмов: гибкий поиск с приоритетом точного совпадения

from rapidfuzz import fuzz                 # для fuzzy-поиска
from utils import normalize_for_match      # функция нормализации текста
from database import fetch_all_originals   # функция получения всех оригиналов из БД

# Глобальные переменные каталога
CATALOG = None
BRAND_MAP = None
NAME_MAP = None

def load_catalog(conn):
    """Загрузка всех оригиналов в память и подготовка словарей для поиска"""
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
    return catalog, brand_map, name_map

def init_catalog(conn):
    """Инициализация глобальных переменных каталога"""
    global CATALOG, BRAND_MAP, NAME_MAP
    CATALOG, BRAND_MAP, NAME_MAP = load_catalog(conn)
def find_original(conn, user_text):
    global CATALOG, BRAND_MAP, NAME_MAP

    if not user_text or not user_text.strip():
        return {"ok": False, "message": "Пустой запрос. Отправь в формате: 'Бренд Название'."}

    if not CATALOG:
        init_catalog(conn)

    user_norm = normalize_for_match(user_text)

    # 1. Сначала точное совпадение brand + name (display_norm)
    for c in CATALOG:
        if c["display_norm"] == user_norm:
            return {"ok": True, "original": c}

    # 2. Fuzzy-поиск по display_norm
    best, score = None, 0
    for c in CATALOG:
        s = fuzz.ratio(user_norm, c["display_norm"])
        if s > score:
            best, score = c, s
    if best and score >= 90:  # порог можно подстроить
        return {"ok": True, "original": best}

    # 3. Fuzzy-поиск только по названию
    best, score = None, 0
    for c in CATALOG:
        s = fuzz.ratio(user_norm, c["name_norm"])
        if s > score:
            best, score = c, s
    if best and score >= 90:
        return {"ok": True, "original": best}

    return {"ok": False, "message": "У меня не получилось найти то, что вы искали. Пожалуйста, попробуйте снова. 😅"}

# perfume-bot/search.py
from rapidfuzz import fuzz
from utils import normalize_for_match
from database import fetch_all_originals

# Глобальные переменные каталога
CATALOG = None

def load_catalog(conn):
    """Загрузка всех оригиналов с клонами в память"""
    rows = fetch_all_originals(conn)
    catalog = []

    for r in rows:
        item = {
            "id": r["id"],
            "brand": r["brand"] or "",
            "name": r["name"] or "",
            "brand_norm": normalize_for_match(r["brand"]),
            "name_norm": normalize_for_match(r["name"]),
            "display_norm": normalize_for_match(f"{r['brand']} {r['name']}"),
            "clones": [normalize_for_match(c) for c in r.get("clones", [])]  # список нормализованных клонов
        }
        catalog.append(item)
    return catalog

def init_catalog(conn):
    """Инициализация глобальных переменных каталога"""
    global CATALOG
    CATALOG = load_catalog(conn)

def find_original(conn, user_text):
    """Поиск оригинала по введенному тексту"""
    global CATALOG
    if not user_text or not user_text.strip():
        return {"ok": False, "message": "Пустой запрос. Отправь в формате: 'Бренд Название'."}

    if not CATALOG:
        init_catalog(conn)

    user_norm = normalize_for_match(user_text)

    # --------- 1. Поиск по оригиналу ----------
    # 1a. Точное совпадение
    for c in CATALOG:
        if c["display_norm"] == user_norm:
            return {"ok": True, "original": c}

    # 1b. Fuzzy по display_norm
    best, score = None, 0
    for c in CATALOG:
        s = fuzz.ratio(user_norm, c["display_norm"])
        if s > score:
            best, score = c, s
    if best and score >= 90:
        return {"ok": True, "original": best}

    # 1c. Fuzzy только по названию
    best, score = None, 0
    for c in CATALOG:
        s = fuzz.ratio(user_norm, c["name_norm"])
        if s > score:
            best, score = c, s
    if best and score >= 90:
        return {"ok": True, "original": best}

    # --------- 2. Поиск по клонам ----------
    best, score = None, 0
    for c in CATALOG:
        for clone_norm in c.get("clones", []):
            s = fuzz.ratio(user_norm, clone_norm)
            if s > score:
                best, score = c, s
    if best and score >= 85:  # чуть ниже порог для поиска по клонам
        return {"ok": True, "original": best}

    # --------- 3. Не нашли ----------
    return {"ok": False, "message": "У меня не получилось найти то, что вы искали. Пожалуйста, попробуйте снова. 😅"}

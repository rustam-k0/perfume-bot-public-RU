# perfume-bot/search.py
# Логика поиска парфюмов с приоритетом точного совпадения

import logging
from rapidfuzz import fuzz
from utils import normalize_for_match
from database import fetch_all_originals, fetch_clones_for_search

# Глобальные каталоги (загружаются один раз)
CATALOG = []
BRAND_MAP = {}
NAME_MAP = {}
CLONE_CATALOG = []

def _load_catalog(conn):
    """Загружает оригиналы и клоны в память, готовит словари для поиска."""
    global CATALOG, BRAND_MAP, NAME_MAP, CLONE_CATALOG
    try:
        rows = fetch_all_originals(conn)
        CATALOG, BRAND_MAP, NAME_MAP = [], {}, {}
        for r in rows:
            brand, name = r["brand"] or "", r["name"] or ""
            item = {
                "id": r["id"],
                "brand": brand,
                "name": name,
                "brand_norm": normalize_for_match(brand),
                "name_norm": normalize_for_match(name),
                "display_norm": normalize_for_match(f"{brand} {name}"),
            }
            CATALOG.append(item)
            BRAND_MAP.setdefault(item["brand_norm"], []).append(item)
            NAME_MAP.setdefault(item["name_norm"], []).append(item)

        clone_rows = fetch_clones_for_search(conn)
        CLONE_CATALOG = [
            {
                "brand": r["brand"] or "",
                "name": r["name"] or "",
                "display_norm": normalize_for_match(f"{r['brand']} {r['name']}"),
                "original_id": r["original_id"],
            }
            for r in clone_rows
        ]
    except Exception as e:
        logging.error(f"Ошибка загрузки каталога: {e}")
        CATALOG, BRAND_MAP, NAME_MAP, CLONE_CATALOG = [], {}, {}, []
        raise

def init_catalog(conn):
    _load_catalog(conn)

def _find_in_catalog(user_norm, space):
    """Ищет ближайшее совпадение в указанном пространстве."""
    best = {"ok": False, "result": None, "score": 0}
    for item in space:
        score = fuzz.ratio(user_norm, item["display_norm"])
        if score > best["score"]:
            best = {"ok": True, "result": item, "score": score}
    return best

def find_original(conn, user_text):
    """Главная функция поиска оригинала по тексту пользователя."""
    global CATALOG

    if not user_text or not user_text.strip():
        return {"ok": False, "message": "Пустой запрос. Отправь в формате: 'Бренд Название'."}

    if not CATALOG:  # ленивое восстановление каталога
        try:
            init_catalog(conn)
        except Exception:
            return {"ok": False, "message": "Ошибка загрузки каталога. Попробуйте позже."}

    user_norm = normalize_for_match(user_text)

    # Точное совпадение
    for item in CATALOG:
        if user_norm == item["display_norm"]:
            return {"ok": True, "original": item}

    # Поиск по каталогу
    match = _find_in_catalog(user_norm, CATALOG)
    if match["ok"] and match["score"] > 70:
        return {"ok": True, "original": match["result"]}

    return {"ok": False, "message": "Не удалось найти аромат. Попробуйте снова. 😅"}

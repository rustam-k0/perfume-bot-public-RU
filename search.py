# perfume-bot/search.py (Улучшенная версия)
# Логика поиска парфюмов: гибкий поиск с приоритетом точного совпадения

from rapidfuzz import fuzz
from utils import normalize_for_match
from database import fetch_all_originals, fetch_clones_for_search, fetch_original_by_id
import logging # Добавлено для внутреннего логирования в случае ошибок

# Глобальные переменные каталога. Загружаются один раз при старте.
CATALOG = None
BRAND_MAP = None
NAME_MAP = None
CLONE_CATALOG = None

def _load_catalog(conn):
    """
    Загрузка всех оригиналов и клонов в память и подготовка словарей для поиска.
    Это приватная функция. Добавлена обработка ошибок.
    """
    global CATALOG, BRAND_MAP, NAME_MAP, CLONE_CATALOG
    
    try:
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

    except Exception as e:
        logging.error(f"Ошибка при загрузке каталога из БД: {e}")
        # Если загрузка не удалась, обнуляем каталоги, чтобы избежать сбоев
        CATALOG = []
        BRAND_MAP = {}
        NAME_MAP = {}
        CLONE_CATALOG = []
        # Важно: поднимаем исключение, чтобы web.py мог его поймать и сообщить о проблеме
        raise 

def init_catalog(conn):
    """Инициализация глобальных переменных каталога."""
    _load_catalog(conn)

def _find_in_catalog(user_text, search_space):
# ... (остальной код без изменений) ...
    # ...
    return {"ok": False, "result": None, "score": 0}

def find_original(conn, user_text):
    """
    Главная функция поиска.
    """
    global CATALOG, BRAND_MAP, NAME_MAP

    if not user_text or not user_text.strip():
        return {"ok": False, "message": "Пустой запрос. Отправь в формате: 'Бренд Название'."}

    # Если каталог пуст, пытаемся инициализировать (на случай, если web.py пропустил)
    if not CATALOG:
        try:
            init_catalog(conn)
        except Exception:
            # Если инициализация не удалась (например, база данных пуста/недоступна)
            return {"ok": False, "message": "Проблема с загрузкой каталога. Попробуйте позже."}

    user_norm = normalize_for_match(user_text)
    user_words = user_norm.split()

    # ... (остальной код find_original без изменений) ...
    
    # Если ничего не найдено
    return {"ok": False, "message": "У меня не получилось найти то, что вы искали. Пожалуйста, попробуйте снова. 😅"}
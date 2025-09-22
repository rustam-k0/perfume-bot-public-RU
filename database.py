# perfume-bot/database.py
# Работа с SQLite и fuzzy-поиск оригиналов

import sqlite3
from rapidfuzz import process, fuzz

def get_connection(path="data/perfumes.db"):
    """Вернуть sqlite3.Connection. check_same_thread=False для использования в многопоточном окружении бота."""
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_all_originals(conn):
    """Вернуть все строки OriginalPerfume."""
    cur = conn.cursor()
    cur.execute("SELECT id, brand, name, price_eur, url FROM OriginalPerfume")
    return cur.fetchall()

def find_best_originals(conn, query, limit=3, score_cutoff=60):
    """
    Fuzzy-поиск оригиналов по строке query.
    Возвращает список словарей: {id, brand, name, score}.
    score_cutoff — минимальная допустимая похожесть (0-100).
    """
    rows = fetch_all_originals(conn)
    choices = []
    ids = []
    for r in rows:
        brand = r["brand"] or ""
        name = r["name"] or ""
        display = (brand + " " + name).strip()
        if not display:
            continue
        choices.append(display)
        ids.append(r["id"])

    if not choices:
        return []

    # Используем token_set_ratio — хорошо для перестановок слов и опечаток
    raw_matches = process.extract(query, choices, scorer=fuzz.token_set_ratio, limit=limit)
    results = []
    for choice_text, score, idx in raw_matches:
        if score >= score_cutoff:
            r = next((x for x in rows if x["id"] == ids[idx]), None)
            if r:
                results.append({"id": ids[idx], "brand": r["brand"], "name": r["name"], "score": score})
    return results

def get_original_by_id(conn, original_id):
    cur = conn.cursor()
    cur.execute("SELECT id, brand, name, price_eur, url FROM OriginalPerfume WHERE id = ?", (original_id,))
    return cur.fetchone()

def get_copies_by_original_id(conn, original_id):
    cur = conn.cursor()
    cur.execute(
        "SELECT id, original_id, brand, name, price_eur, url, notes, saved_amount FROM CopyPerfume WHERE original_id = ?",
        (original_id,),
    )
    return cur.fetchall()

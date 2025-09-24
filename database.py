# perfume-bot/database.py
# Модуль для работы с базой данных SQLite.

import sqlite3

def get_connection(path="data/perfumes.db"):
    """
    Возвращает объект подключения к SQLite.
    check_same_thread=False позволяет использовать подключение
    в многопоточном окружении бота.
    """
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_all_originals(conn):
    """
    Извлекает все записи из таблицы OriginalPerfume.
    """
    cur = conn.cursor()
    cur.execute("SELECT id, brand, name FROM OriginalPerfume")
    return cur.fetchall()

def fetch_clones_for_search(conn):
    """
    Извлекает все записи из таблицы CopyPerfume, которые нужны для поиска.
    """
    cur = conn.cursor()
    cur.execute("SELECT brand, name, original_id FROM CopyPerfume")
    return cur.fetchall()

def fetch_original_by_id(conn, original_id):
    """
    Извлекает один оригинальный парфюм по его уникальному ID.
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT id, brand, name, price_eur, url FROM OriginalPerfume WHERE id = ?",
        (original_id,),
    )
    return cur.fetchone()

def get_copies_by_original_id(conn, original_id):
    """
    Извлекает все копии, связанные с заданным оригиналом.
    """
    cur = conn.cursor()
    cur.execute(
        "SELECT id, original_id, brand, name, price_eur, url, notes, saved_amount FROM CopyPerfume WHERE original_id = ?",
        (original_id,),
    )
    return cur.fetchall()
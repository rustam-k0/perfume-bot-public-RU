# perfume-bot/database.py
# Модуль для работы с базой данных SQLite.

import sqlite3

def dict_factory(cursor, row):
    """Преобразует строки из базы данных в полноценные словари."""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def connect_db(path="data/perfumes.db"):
    """
    Возвращает объект подключения к SQLite с фабрикой словарей.
    check_same_thread=False позволяет использовать подключение в многопоточном окружении.
    """
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = dict_factory  # Используем нашу фабрику
    return conn

def fetch_all_originals(conn):
    """Извлекает все оригиналы для кэширования в search.py."""
    cur = conn.cursor()
    cur.execute("SELECT id, brand, name FROM OriginalPerfume")
    return cur.fetchall()

def fetch_clones_for_search(conn):
    """Извлекает все клоны для кэширования в search.py."""
    cur = conn.cursor()
    cur.execute("SELECT brand, name, original_id FROM CopyPerfume")
    return cur.fetchall()

def fetch_original_by_id(conn, original_id):
    """Извлекает один оригинальный парфюм по его ID (может быть полезно для других целей)."""
    cur = conn.cursor()
    cur.execute(
        "SELECT id, brand, name, price_eur, url FROM OriginalPerfume WHERE id = ?",
        (original_id,),
    )
    return cur.fetchone()

def fetch_clones_by_original_id(conn, original_id):
    """Извлекает все копии, связанные с заданным оригиналом."""
    cur = conn.cursor()
    cur.execute(
        "SELECT id, original_id, brand, name, price_eur, url, notes, saved_amount FROM CopyPerfume WHERE original_id = ?",
        (original_id,),
    )
    return cur.fetchall()
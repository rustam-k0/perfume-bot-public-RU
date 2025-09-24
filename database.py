# perfume-bot/database.py
# Модуль для работы с базой данных SQLite.

import sqlite3
import time

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

def log_message(conn, user_id, message, status, notes=""):
    """
    Логирует сообщение пользователя в таблицу UserMessages.
    """
    cursor = conn.cursor()
    # Проверяем, существует ли таблица, и создаём, если нет.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserMessages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT
        )
    """)
    cursor.execute(
        "INSERT INTO UserMessages (user_id, timestamp, message, status, notes) VALUES (?, ?, ?, ?, ?)",
        (user_id, int(time.time()), message, status, notes)
    )
    conn.commit()
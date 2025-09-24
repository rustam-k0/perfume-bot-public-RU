# perfume-bot/database.py
# Модуль для работы с базой данных SQLite.

import sqlite3
import time

def get_connection(path="data/perfumes.db"):
    # ... (код без изменений) ...
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db_if_not_exists(conn):
    """
    Инициализирует базу данных, создавая все необходимые таблицы, если они не существуют.
    """
    cursor = conn.cursor()

    # Таблица для логов сообщений
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

    # Таблица для оригиналов (ваша существующая таблица)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS OriginalPerfume (
            id TEXT PRIMARY KEY,
            brand TEXT,
            name TEXT,
            price_eur REAL,
            url TEXT
        )
    """)

    # Таблица для клонов (ваша существующая таблица)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CopyPerfume (
            id TEXT PRIMARY KEY,
            original_id TEXT,
            brand TEXT,
            name TEXT,
            price_eur REAL,
            url TEXT,
            notes TEXT,
            saved_amount REAL,
            FOREIGN KEY(original_id) REFERENCES OriginalPerfume(id)
        )
    """)

    conn.commit()


def fetch_all_originals(conn):
    # ... (код без изменений) ...
    cur = conn.cursor()
    cur.execute("SELECT id, brand, name FROM OriginalPerfume")
    return cur.fetchall()

def fetch_clones_for_search(conn):
    # ... (код без изменений) ...
    cur = conn.cursor()
    cur.execute("SELECT brand, name, original_id FROM CopyPerfume")
    return cur.fetchall()

def fetch_original_by_id(conn, original_id):
    # ... (код без изменений) ...
    cur = conn.cursor()
    cur.execute(
        "SELECT id, brand, name, price_eur, url FROM OriginalPerfume WHERE id = ?",
        (original_id,),
    )
    return cur.fetchone()

def get_copies_by_original_id(conn, original_id):
    # ... (код без изменений) ...
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
    cursor.execute(
        "INSERT INTO UserMessages (user_id, timestamp, message, status, notes) VALUES (?, ?, ?, ?, ?)",
        (user_id, int(time.time()), message, status, notes)
    )
    conn.commit()
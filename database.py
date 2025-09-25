# perfume-bot/database.py
# Работа с базой данных SQLite

import sqlite3
import time

def get_connection(path="data/perfumes.db"):
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db_if_not_exists(conn):
    """Создаёт таблицы, если они ещё не существуют."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS UserMessages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS OriginalPerfume (
            id TEXT PRIMARY KEY,
            brand TEXT,
            name TEXT,
            price_eur REAL,
            url TEXT
        );

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
        );
    """)
    conn.commit()

def fetch_all_originals(conn):
    return conn.execute("SELECT id, brand, name FROM OriginalPerfume").fetchall()

def fetch_clones_for_search(conn):
    return conn.execute("SELECT brand, name, original_id FROM CopyPerfume").fetchall()

def fetch_original_by_id(conn, original_id):
    return conn.execute(
        "SELECT id, brand, name, price_eur, url FROM OriginalPerfume WHERE id = ?",
        (original_id,)
    ).fetchone()

def get_copies_by_original_id(conn, original_id):
    return conn.execute(
        "SELECT id, original_id, brand, name, price_eur, url, notes, saved_amount "
        "FROM CopyPerfume WHERE original_id = ?",
        (original_id,)
    ).fetchall()

def log_message(conn, user_id, message, status, notes=""):
    """Сохраняет сообщение пользователя в UserMessages."""
    with conn:
        conn.execute(
            "INSERT INTO UserMessages (user_id, timestamp, message, status, notes) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, int(time.time()), message, status, notes)
        )

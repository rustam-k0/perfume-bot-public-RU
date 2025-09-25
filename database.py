# perfume-bot/database.py (Финальная исправленная версия)

import sqlite3
import time
import sys
import os

# Путь к БД не требует создания папки, так как вы подтвердили ее существование.

def get_connection(path="data/perfumes.db"):
    """
    Возвращает соединение с базой данных SQLite.
    Добавлена обработка критической ошибки подключения.
    """
    try:
        # check_same_thread=False необходим для Flask/вебхуков
        conn = sqlite3.connect(path, check_same_thread=False) 
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось подключиться к базе данных {path}: {e}")
        # Если нет подключения, нет смысла запускать бота
        sys.exit(1) 

def init_db_if_not_exists(conn):
    """
    Создаёт все необходимые таблицы, включая UserMessages, если они ещё не существуют.
    """
    conn.executescript("""
        -- ТАБЛИЦА ДЛЯ ЛОГИРОВАНИЯ: UserMessages
        CREATE TABLE IF NOT EXISTS UserMessages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL,
            notes TEXT
        );

        -- СУЩЕСТВУЮЩИЕ ТАБЛИЦЫ: OriginalPerfume
        CREATE TABLE IF NOT EXISTS OriginalPerfume (
            id TEXT PRIMARY KEY, brand TEXT, name TEXT, price_eur REAL, url TEXT
        );

        -- СУЩЕСТВУЮЩИЕ ТАБЛИЦЫ: CopyPerfume
        CREATE TABLE IF NOT EXISTS CopyPerfume (
            id TEXT PRIMARY KEY,
            original_id TEXT, brand TEXT, name TEXT, price_eur REAL, url TEXT,
            notes TEXT, saved_amount REAL,
            FOREIGN KEY(original_id) REFERENCES OriginalPerfume(id)
        );
    """)
    conn.commit()

# --- ФУНКЦИИ, ИСПОЛЬЗУЕМЫЕ В search.py ---

def fetch_all_originals(conn):
    return conn.execute("SELECT id, brand, name FROM OriginalPerfume").fetchall()

def fetch_clones_for_search(conn):
    return conn.execute("SELECT brand, name, original_id FROM CopyPerfume").fetchall()

def fetch_original_by_id(conn, original_id):
    return conn.execute(
        "SELECT id, brand, name, price_eur, url FROM OriginalPerfume WHERE id = ?",
        (original_id,)
    ).fetchone()

# --- ФУНКЦИЯ, КОТОРАЯ ВЫЗЫВАЛА ОШИБКУ ИМПОРТА В web.py ---

def get_copies_by_original_id(conn, original_id): 
    """Получает все копии для конкретного оригинала."""
    return conn.execute(
        "SELECT id, original_id, brand, name, price_eur, url, notes, saved_amount "
        "FROM CopyPerfume WHERE original_id = ?",
        (original_id,)
    ).fetchall()

# --- ФУНКЦИЯ ДЛЯ ЛОГИРОВАНИЯ ---

def log_message(conn, user_id, message, status, notes=""):
    """
    Сохраняет сообщение пользователя в UserMessages.
    Использует обработку ошибок, чтобы не ломать основной функционал.
    """
    try:
        timestamp = int(time.time())
        conn.execute(
            "INSERT INTO UserMessages (user_id, timestamp, message, status, notes) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, timestamp, message, status, notes)
        )
        conn.commit()
    except sqlite3.Error as e:
        # Если не удалось записать лог, бот продолжит работать
        print(f"ПРЕДУПРЕЖДЕНИЕ: Ошибка при записи лога для пользователя {user_id}: {e}")
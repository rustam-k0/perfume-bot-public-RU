# perfume-bot/database.py (Финальная, надёжная версия)

import sqlite3
import time
import os
# import logging # Убран, чтобы не усложнять, но в реальном проекте его лучше оставить

def ensure_data_directory():
    """СОЗДАЕТ ДИРЕКТОРИЮ data/, ЕСЛИ ОНА НЕ СУЩЕСТВУЕТ."""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"INFO: Создана директория: {data_dir}")

def get_connection(path="data/perfumes.db"):
    """Возвращает соединение с базой данных SQLite."""
    try:
        ensure_data_directory() # ГАРАНТИЯ: Папка data/ существует
        
        # Если вы используете Flask/Webhook, check_same_thread=False необходимо
        conn = sqlite3.connect(path, check_same_thread=False) 
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: Не удалось подключиться к базе данных {path}: {e}")
        raise # Остановка, если нет подключения

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
            id TEXT PRIMARY KEY, brand TEXT, name TEXT, price_eur REAL, url TEXT
        );

        CREATE TABLE IF NOT EXISTS CopyPerfume (
            id TEXT PRIMARY KEY,
            original_id TEXT, brand TEXT, name TEXT, price_eur REAL, url TEXT,
            notes TEXT, saved_amount REAL,
            FOREIGN KEY(original_id) REFERENCES OriginalPerfume(id)
        );
    """)
    conn.commit()
    # print("INFO: Все таблицы БД проверены/созданы.")


# ... (функции fetch_all_originals, fetch_clones_for_search, fetch_original_by_id, get_copies_by_original_id без изменений) ...


def log_message(conn, user_id, message, status, notes=""):
    """
    Сохраняет сообщение пользователя в UserMessages.
    Использует явную обработку ошибок, чтобы не ломать основной функционал.
    """
    try:
        timestamp = int(time.time())
        conn.execute(
            "INSERT INTO UserMessages (user_id, timestamp, message, status, notes) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, timestamp, message, status, notes)
        )
        conn.commit() # Явный commit для гарантированной записи
    except sqlite3.Error as e:
        # ВАЖНО: Мы поймали ошибку SQL, но не поднимаем ее, чтобы бот продолжал работать
        print(f"ПРЕДУПРЕЖДЕНИЕ: Ошибка при записи лога для пользователя {user_id}: {e}")
    # finally: conn.close() не нужен, так как соединение общее
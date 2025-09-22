# database.py

import sqlite3

# --- Настройка и создание таблиц ---

def setup_database():
    """Создает таблицы в базе данных, если их еще нет."""
    # Подключаемся к файлу data/perfumes.db
    conn = sqlite3.connect('data/perfumes.db')
    cursor = conn.cursor()

    # Создаем таблицу для оригинальных парфюмов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OriginalPerfume (
        id TEXT PRIMARY KEY,
        brand TEXT NOT NULL,
        name TEXT NOT NULL,
        price_eur REAL NOT NULL,
        url TEXT
    )
    ''')

    # Создаем таблицу для клонов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CopyPerfume (
        id TEXT PRIMARY KEY,
        original_id TEXT,
        brand TEXT NOT NULL,
        name TEXT NOT NULL,
        price_eur REAL NOT NULL,
        url TEXT,
        notes TEXT,
        saved_amount REAL,
        FOREIGN KEY (original_id) REFERENCES OriginalPerfume (id)
    )
    ''')
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
    print("База данных успешно настроена.")


# --- Функции для поиска данных ---

def get_all_original_perfumes():
    """Возвращает список всех оригинальных парфюмов (бренд + название)."""
    conn = sqlite3.connect('data/perfumes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT brand, name FROM OriginalPerfume")
    # Превращаем результат в список строк вида "Dior Sauvage"
    perfumes = [f"{row[0]} {row[1]}" for row in cursor.fetchall()]
    conn.close()
    return perfumes


def find_perfume_and_clones(full_name):
    """Находит оригинал и все его клоны по полному названию."""
    conn = sqlite3.connect('data/perfumes.db')
    # Позволяет получать результаты в виде словарей (удобнее)
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()

    # Разделяем "Бренд Название" обратно
    brand, name = full_name.split(' ', 1)
    
    # Находим оригинал
    cursor.execute("SELECT * FROM OriginalPerfume WHERE brand = ? AND name = ?", (brand, name))
    original = cursor.fetchone()

    if not original:
        conn.close()
        return None, []

    # Находим все его клоны
    cursor.execute("SELECT * FROM CopyPerfume WHERE original_id = ?", (original['id'],))
    clones = cursor.fetchall()
    
    conn.close()
    return original, clones
# normalize_perfumes.py (ИСПРАВЛЕННАЯ ВЕРСИЯ)

import csv  # Работа с CSV-файлами
import sqlite3  # Работа с SQLite базой данных
import os  # Работа с файловой системой

# --- Константы ---
DATA_DIR = 'data'  # Папка, где лежат CSV и база
CSV_FILE = os.path.join(DATA_DIR, 'perfumes_master.csv')  # Путь к CSV-файлу
DB_FILE = os.path.join(DATA_DIR, 'perfumes.db')  # Путь к SQLite базе

def setup_database(cursor):
    """Создает таблицы и индексы в базе данных."""
    # Таблица для оригинальных парфюмов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OriginalPerfume (
        id TEXT PRIMARY KEY,  # Уникальный идентификатор оригинала
        brand TEXT,  # Бренд оригинала
        name TEXT,  # Название оригинала
        price_eur REAL,  # Цена в евро
        url TEXT  # Ссылка на оригинал
    )
    ''')
    
    # Таблица для парфюмов-копий
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CopyPerfume (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  # Автоинкрементный ID копии
        original_id TEXT,  # Ссылка на оригинал
        brand TEXT,  # Бренд копии
        name TEXT,  # Название копии
        price_eur REAL,  # Цена копии в евро
        url TEXT,  # Ссылка на копию
        notes TEXT,  # Доп. заметки
        saved_amount REAL,  # Сколько сэкономлено по сравнению с оригиналом
        FOREIGN KEY (original_id) REFERENCES OriginalPerfume(id)  # Связь с оригиналом
    )
    ''')
    
    # Индекс для ускорения поиска копий по оригиналу
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_copy_original_id ON CopyPerfume(original_id)')
    print("Структура базы данных успешно создана.")

def clean_value(value):
    """Преобразует пустые строки в None."""
    return None if not value or value.strip() == '' else value  # Если пустая строка или None → None

def to_float(value):
    """Безопасно преобразует значение во float, возвращает None в случае ошибки."""
    if value is None:
        return None  # Если нет значения, возвращаем None
    try:
        return float(value)  # Пробуем преобразовать в float
    except (ValueError, TypeError):
        return None  # При ошибке преобразования возвращаем None

def process_data():
    """Основная функция для чтения CSV и записи данных в SQLite."""
    os.makedirs(DATA_DIR, exist_ok=True)  # Создает папку data, если нет
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)  # Удаляет старую базу, если она есть
        
    conn = sqlite3.connect(DB_FILE)  # Создает соединение с базой
    cursor = conn.cursor()  # Получаем курсор для выполнения SQL
    
    setup_database(cursor)  # Создаем таблицы и индексы
    
    # Словарь для хранения ID уже добавленных оригиналов
    # Ключ: (бренд, название), Значение: id
    original_id_map = {}
    
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as file:  # Открываем CSV
            reader = csv.DictReader(file)  # Читаем строки как словари
            
            for row in reader:  # Проходим по каждой строке CSV
                og_brand = clean_value(row.get('og_brand'))  # Чистим бренд оригинала
                og_name = clean_value(row.get('og_name'))  # Чистим название оригинала
                
                if not og_brand or not og_name:
                    continue  # Пропускаем строки без бренда или названия
                
                original_key = (og_brand, og_name)  # Ключ для карты оригиналов
                
                # --- 1. Обработка оригинала ---
                if original_key not in original_id_map:  # Если оригинал еще не добавлен
                    original_id_for_db = clean_value(row.get('id'))  # Берем ID оригинала
                    
                    if not original_id_for_db:
                        continue  # Пропускаем без ID

                    original_data = (
                        original_id_for_db,  # ID
                        og_brand,  # Бренд
                        og_name,  # Название
                        to_float(clean_value(row.get('og_price_eur'))),  # Цена, float или None
                        clean_value(row.get('og_url'))  # Ссылка
                    )
                    cursor.execute(
                        "INSERT INTO OriginalPerfume (id, brand, name, price_eur, url) VALUES (?, ?, ?, ?, ?)",
                        original_data  # Добавляем оригинал в базу
                    )
                    original_id_map[original_key] = original_id_for_db  # Сохраняем ID в карту
                
                # --- 2. Обработка копии ---
                correct_original_id = original_id_map[original_key]  # Берем правильный ID оригинала

                copy_data = (
                    correct_original_id,  # ID оригинала
                    clean_value(row.get('copy_brand')),  # Бренд копии
                    clean_value(row.get('copy_name')),  # Название копии
                    to_float(clean_value(row.get('copy_price_eur'))),  # Цена копии
                    clean_value(row.get('copy_url')),  # Ссылка копии
                    clean_value(row.get('notes')),  # Заметки
                    to_float(clean_value(row.get('saved_amount')))  # Сколько сэкономлено
                )
                cursor.execute(
                    """
                    INSERT INTO CopyPerfume 
                    (original_id, brand, name, price_eur, url, notes, saved_amount) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    copy_data  # Добавляем копию в базу
                )

        conn.commit()  # Сохраняем изменения в базе
        print(f"Данные успешно импортированы. Добавлено {len(original_id_map)} уникальных оригиналов.")
        
    except FileNotFoundError:
        print(f"Ошибка: файл {CSV_FILE} не найден.")  # Если CSV нет
    except Exception as e:
        print(f"Произошла ошибка: {e}")  # Ловим другие ошибки
        conn.rollback()  # Откатываем транзакцию
    finally:
        conn.close()  # Закрываем соединение с базой

if __name__ == "__main__":
    process_data()  # Запускаем обработку данных

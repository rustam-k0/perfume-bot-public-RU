# check.py

import sqlite3
import os

# Имя файла базы данных
DB_FILE = 'data/perfumes.db'

def check_database_integrity():
    """
    Проверяет существование файла БД и выводит содержимое таблиц.
    Эта версия НЕ изменяет и НЕ удаляет ваши данные.
    """
    # Проверяем, существует ли файл базы данных
    if not os.path.exists(DB_FILE):
        print(f"❌ Ошибка: Файл базы данных не найден по пути: {DB_FILE}")
        print("Пожалуйста, убедитесь, что база данных находится в папке data/.")
        return

    print(f"✅ Файл базы данных найден: {DB_FILE}")
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # --- Проверяем и выводим содержимое таблицы OriginalPerfume ---
        print("\n--- 🧐 Содержимое таблицы OriginalPerfume ---")
        cursor.execute("SELECT * FROM OriginalPerfume LIMIT 5") # LIMIT 5 чтобы не выводить тысячи строк
        originals = cursor.fetchall()
        
        if not originals:
            print("Таблица OriginalPerfume пуста.")
        else:
            for row in originals:
                print(row)
        
        # --- Проверяем и выводим содержимое таблицы CopyPerfume ---
        print("\n--- 🧐 Содержимое таблицы CopyPerfume ---")
        cursor.execute("SELECT * FROM CopyPerfume LIMIT 5")
        clones = cursor.fetchall()

        if not clones:
            print("Таблица CopyPerfume пуста.")
        else:
            for row in clones:
                print(row)
                
        conn.close()
        print("\n👍 Проверка завершена. Ошибок не найдено.")

    except sqlite3.Error as e:
        print(f"❌ Произошла ошибка SQLite: {e}")


if __name__ == "__main__":
    check_database_integrity()
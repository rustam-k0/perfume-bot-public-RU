# check.py (обновленная и расширенная версия)

import sqlite3  # Работа с SQLite базой данных
import os  # Работа с файловой системой

DB_FILE = os.path.join('data', 'perfumes.db')  # Путь к базе данных

def print_header(title):
    """Печатает красивый заголовок для каждого блока проверки."""
    print("\n" + "="*50)  # Разделитель сверху
    print(f"🔎 {title}")  # Заголовок блока с эмодзи
    print("="*50)  # Разделитель снизу

def check_database():
    """Подключается к БД и выполняет набор проверок."""
    if not os.path.exists(DB_FILE):
        print(f"Файл базы данных {DB_FILE} не найден. Сначала запустите normalize_perfumes.py.")
        return  # Если базы нет, выходим

    conn = sqlite3.connect(DB_FILE)  # Подключение к базе
    conn.row_factory = sqlite3.Row  # Позволяет обращаться к колонкам по имени
    cursor = conn.cursor()  # Получаем курсор для выполнения SQL

    try:
        # --- 1. Общая статистика ---
        print_header("Общая статистика")  # Заголовок блока
        cursor.execute("SELECT COUNT(*) FROM OriginalPerfume")  # Считаем все оригиналы
        total_originals = cursor.fetchone()[0]  # Берем результат
        print(f"✅ Всего оригинальных парфюмов: {total_originals}")  # Выводим

        cursor.execute("SELECT COUNT(*) FROM CopyPerfume")  # Считаем все копии
        total_copies = cursor.fetchone()[0]  # Берем результат
        print(f"✅ Всего копий: {total_copies}")  # Выводим

        # --- 2. Проверка копий для 'Chanel Coco Mademoiselle' ---
        print_header("Копии для 'Chanel Coco Mademoiselle'")  # Заголовок
        query_chanel = """
        SELECT cp.brand, cp.name, cp.price_eur
        FROM CopyPerfume AS cp
        JOIN OriginalPerfume AS op ON cp.original_id = op.id
        WHERE op.brand = ? AND op.name = ?
        """
        cursor.execute(query_chanel, ('Chanel', 'Coco Mademoiselle'))  # Параметризованный запрос
        chanel_copies = cursor.fetchall()  # Получаем все результаты
        print(f"Найдено копий: {len(chanel_copies)}")  # Считаем количество
        for copy in chanel_copies:
            price_str = f"{copy['price_eur']} EUR" if copy['price_eur'] is not None else "N/A"
            print(f"  - {copy['brand']} / {copy['name']} ({price_str})")  # Печатаем бренд, название, цену

        # --- 3. Все оригиналы от Tom Ford ---
        print_header("Оригинальные ароматы от 'Tom Ford'")
        cursor.execute("SELECT name FROM OriginalPerfume WHERE brand = ? ORDER BY name", ('Tom Ford',))  # Запрос по бренду
        tom_ford_originals = cursor.fetchall()  # Получаем результат
        print(f"Найдено ароматов от Tom Ford: {len(tom_ford_originals)}")  # Количество
        for original in tom_ford_originals:
            print(f"  - {original['name']}")  # Печатаем название

        # --- 4. Поиск бренда для копий L'aventure ---
        print_header("Поиск бренда для копий 'L'aventure' и 'L'aventure Intense'")
        adventure_names = ('L\'aventure', 'L\'aventure Intense')  # Список названий
        cursor.execute(f"SELECT brand, name FROM CopyPerfume WHERE name IN (?, ?)", adventure_names)  # Параметризованный запрос
        adventure_copies = cursor.fetchall()  # Получаем результат
        if adventure_copies:
            print(f"Найдены следующие совпадения:")
            for copy in adventure_copies:
                print(f"  - Бренд: {copy['brand']}, Название: {copy['name']}")  # Печатаем бренд и название
        else:
            print("Копии с названием 'L'aventure' или 'L'aventure Intense' не найдены.")  # Если нет

        # --- 5. Все копии для 'Silver Mountain Water' от Creed ---
        print_header("Копии для 'Creed Silver Mountain Water'")
        query_creed = """
        SELECT cp.brand, cp.name
        FROM CopyPerfume AS cp
        JOIN OriginalPerfume AS op ON cp.original_id = op.id
        WHERE op.brand = ? AND op.name = ?
        """
        cursor.execute(query_creed, ('Creed', 'Silver Mountain Water'))  # Запрос по оригиналу
        smw_copies = cursor.fetchall()  # Получаем все копии
        if smw_copies:
            print(f"Найдено копий: {len(smw_copies)}")  # Количество
            for copy in smw_copies:
                print(f"  - {copy['brand']} / {copy['name']}")  # Печатаем бренд и название
        else:
            print("Копии для 'Creed Silver Mountain Water' не найдены.")  # Если нет

        # --- 6. Топ-5 оригиналов с наибольшим количеством копий ---
        print_header("Топ-5 оригиналов по количеству копий")
        query_top5 = """
        SELECT op.brand, op.name, COUNT(cp.id) AS copy_count
        FROM OriginalPerfume AS op
        JOIN CopyPerfume AS cp ON op.id = cp.original_id
        GROUP BY op.id
        ORDER BY copy_count DESC
        LIMIT 5
        """
        cursor.execute(query_top5)  # Запрос топ-5
        top_originals = cursor.fetchall()  # Получаем результат
        for idx, item in enumerate(top_originals):
            print(f"  {idx+1}. {item['brand']} / {item['name']} - {item['copy_count']} копий")  # Печатаем позицию, бренд, название, количество копий

        # --- 7. Оригиналы без копий ---
        print_header("Оригиналы без единой копии в базе")
        query_no_copies = """
        SELECT COUNT(*) 
        FROM OriginalPerfume 
        WHERE id NOT IN (SELECT DISTINCT original_id FROM CopyPerfume WHERE original_id IS NOT NULL)
        """
        cursor.execute(query_no_copies)  # Подсчет оригиналов без копий
        no_copies_count = cursor.fetchone()[0]  # Получаем количество
        print(f"Найдено {no_copies_count} оригиналов, для которых нет ни одной копии.")  # Печатаем

    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")  # Ловим ошибки SQLite
    finally:
        conn.close()  # Закрываем соединение с базой

if __name__ == "__main__":
    check_database()  # Запускаем проверки

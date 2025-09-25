import sqlite3

# Список пар "Бренд - Название", к которым нужно добавить ⭐
# Формат: {'brand': 'Название', 'name': 'Название аромата'}
recommended_perfumes = [
    {'brand': 'Mont Blanc', 'name': 'Legend Edt/Edp'},
    {'brand': 'Paris Corner', 'name': 'Killer Oud Jubilant'},
    {'brand': 'Khadlaj Perfumes', 'name': 'Shiyaaka'},
    {'brand': 'Paris Corner', 'name': 'Killer Killer Oud Revolution'},
    {'brand': 'Rue Broca', 'name': 'Theoreme Homme'},
    {'brand': 'Maison Alhambra', 'name': 'Exclusif Tabac'},
    {'brand': 'Afnan', 'name': 'Tobacco Rush'},
    {'brand': 'Ard Al Zaafaran', 'name': 'Dirgham Limited Edition'},
    {'brand': 'Usa Inspired Fragrances', 'name': 'Fragrances- Allure Men Intense'},
    {'brand': 'Maison Alhambra', 'name': 'Blue De Chance'},
    {'brand': 'Geparlys Parfums', 'name': 'Yes I Am the King Le Parfum'},
    {'brand': 'Afnan', 'name': 'Historic Olmeda'},
    {'brand': 'Armaf', 'name': 'Club De Nuit Intense Men Edt/edp/limited Edition'},
    {'brand': 'Al Haramain', 'name': 'L\'aventure (original/intense)'},
    {'brand': 'Armaf', 'name': 'Supremacy Silver'},
    {'brand': 'Lattafa', 'name': 'Raghba for Men'},
    {'brand': 'Armaf', 'name': 'Club De Nuit Sillage'},
    {'brand': 'Alexandria Fragrances', 'name': 'Ete Sauvage Elixir'},
    {'brand': 'Paris Corner', 'name': 'Pendora Scents Saviour Elixir'},
    {'brand': 'Fragrance World', 'name': 'Enigma Une'},
    {'brand': 'Victorinox', 'name': 'Swiss Army Black Steel Edt'},
    {'brand': 'Frank Olivier', 'name': 'Sun Java Intense'},
    {'brand': 'Armaf', 'name': 'Odyssey Homme White'},
    {'brand': 'Geparlys Parfums', 'name': 'Yes I Am the King Icon'},
    {'brand': 'Ard Al Zaafaran', 'name': 'Oud 24 Hrs Gold'},
    {'brand': 'Fragrance World', 'name': 'French Portrait'},
    {'brand': 'Ard Al Zaafaran', 'name': 'Jazzab Silver'},
    {'brand': 'Lattafa', 'name': 'Suqraat'},
    {'brand': 'Lattafa', 'name': 'Bade\'e Al Oud Amethyst'},
    {'brand': 'Afnan', 'name': 'Supremacy in Oud'}
]

def update_database_with_star_in_brand():
    """
    Обновляет базу данных:
    1. Очищает все существующие звёзды из полей brand и name.
    2. Добавляет ⭐ в начало поля 'brand' для рекомендованных ароматов.
    """
    DB_PATH = 'data/perfumes.db'
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("🔄 Шаг 1: Сброс. Удаление всех существующих звёзд '⭐ ' из полей brand и name...")
        # Удаление звёзд из brand (на случай, если они там уже есть)
        cursor.execute("UPDATE CopyPerfume SET brand = REPLACE(brand, '⭐ ', '') WHERE brand LIKE '⭐ %'")
        # Удаление звёзд из name (на случай, если они там остались от прошлых запусков)
        cursor.execute("UPDATE CopyPerfume SET name = REPLACE(name, '⭐ ', '') WHERE name LIKE '⭐ %'")
        conn.commit()
        print("✅ Сброс завершен.")

        print("\n✨ Шаг 2: Добавление '⭐ ' в начало поля brand для рекомендованных ароматов...")
        updated_count = 0
        for item in recommended_perfumes:
            brand_to_search = item['brand']
            name_to_search = item['name']
            
            # Находим записи, используя частичное совпадение по name и точное по brand
            cursor.execute(
                "SELECT id FROM CopyPerfume WHERE brand = ? AND name LIKE ?",
                (brand_to_search, f"%{name_to_search}%")
            )
            records = cursor.fetchall()

            if records:
                # Обновляем поле brand: добавляем '⭐ ' в начало
                # Важно: используем LIKE, чтобы обновить все найденные записи
                cursor.execute(
                    "UPDATE CopyPerfume SET brand = '⭐ ' || brand WHERE brand = ? AND name LIKE ?",
                    (brand_to_search, f"%{name_to_search}%")
                )
                
                # Дополнительно убедимся, что в name нет звезды
                cursor.execute(
                    "UPDATE CopyPerfume SET name = REPLACE(name, '⭐ ', '') WHERE brand LIKE '⭐ ' || ? AND name LIKE ?",
                    (brand_to_search, f"%{name_to_search}%")
                )
                
                updated_count += cursor.rowcount
                print(f"Обновлена запись: {brand_to_search} - {name_to_search}")
            else:
                print(f"Запись не найдена, пропущено: {brand_to_search} - {name_to_search}")
        
        conn.commit()
        print(f"\nОбновление завершено. Всего обновлено записей: {updated_count}")
        
    except sqlite3.Error as e:
        print(f"Произошла ошибка SQLite: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    update_database_with_star_in_brand()
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

def update_database_with_star():
    """Обновляет базу данных, добавляя ⭐ к названиям рекомендованных парфюмов,
       предварительно удаляя лишние звёзды."""
    try:
        conn = sqlite3.connect('data/perfumes.db')
        cursor = conn.cursor()

        # Шаг 1: Удаляем все звёзды из названий
        cursor.execute("UPDATE CopyPerfume SET name = REPLACE(name, '⭐ ', '')")
        conn.commit()
        print("✅ Удалены все существующие звёзды из названий.")

        # Шаг 2: Добавляем одну звезду к нужным записям
        updated_count = 0
        for item in recommended_perfumes:
            brand_to_update = item['brand']
            name_to_search = item['name']
            
            # Используем LIKE для поиска частичного совпадения в названии
            cursor.execute(
                "SELECT id, name FROM CopyPerfume WHERE brand = ? AND name LIKE ?",
                (brand_to_update, f"%{name_to_search}%")
            )
            existing_record = cursor.fetchone()

            if existing_record:
                existing_name = existing_record[1]
                # Проверяем, что звезды ещё нет, и добавляем её
                if not existing_name.startswith('⭐ '):
                    cursor.execute(
                        "UPDATE CopyPerfume SET name = '⭐ ' || name WHERE brand = ? AND name LIKE ?",
                        (brand_to_update, f"%{name_to_search}%")
                    )
                    updated_count += cursor.rowcount
                    print(f"Обновлена запись: {brand_to_update} - {name_to_search}")
            else:
                print(f"Запись не найдена, пропущено: {brand_to_update} - {name_to_search}")
        
        conn.commit()
        print(f"\nОбновление завершено. Всего обновлено записей: {updated_count}")
        
    except sqlite3.Error as e:
        print(f"Произошла ошибка SQLite: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    update_database_with_star()
import csv
import os
import re
from difflib import SequenceMatcher

def normalize_text(text):
    """
    Нормализует текст для сравнения дубликатов:
    - убирает лишние пробелы
    - приводит к нижнему регистру
    - заменяет цифры на слова (простые случаи)
    - убирает знаки препинания
    """
    if not text:
        return ""
    
    text = text.lower().strip()
    
    # Заменяем распространенные цифры на слова
    replacements = {
        '2': 'two', '3': 'three', '4': 'four', '5': 'five',
        '1': 'one', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'
    }
    
    for digit, word in replacements.items():
        text = text.replace(digit, word)
    
    # Убираем знаки препинания и лишние пробелы
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def texts_are_similar(text1, text2, threshold=0.85):
    """
    Проверяет, похожи ли два текста (для определения дубликатов)
    """
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    
    if not norm1 or not norm2:
        return False
    
    similarity = SequenceMatcher(None, norm1, norm2).ratio()
    return similarity >= threshold

def get_text_length_score(text):
    """
    Возвращает "длину" текста для выбора лучшего дубликата
    """
    if not text:
        return 0
    return len(text.strip())

def clean_csv_data():
    """
    Основная функция для обработки CSV файла
    """
    input_file = 'data/perfumes_master.csv'
    output_file = 'data/perfumes_master_new.csv'
    
    # Список всех возможных copy_brand для поиска
    copy_brands = [
        'Armaf', 'Lattafa', 'Maison Alhambra', 'Paris Corner', 'Fragrance World', 
        'Afnan', 'Rasasi', 'Swiss Arabian', 'Ard Al Zaafaran', 'Ajmal', 'La Rive', 
        'Milton Lloyd', 'Smart Collection', 'Geparlys', 'Jenny Glow', 'Cuba', 
        'Avon', 'Zara', 'Next', 'Primark', 'M&S (Marks & Spencer)', 'Aldi', 
        'Lacura', 'Essense Vault', 'Legesi Homme', 'Pharmacia', 'Lidi', 'Oakcha', 
        'Dossier', 'Orientica', 'Just Jack', 'Riiffs', 'LRF (Luxury Fragrance)', 
        'Sapil', 'Ana Abiyedh', 'Amraf', 'Amberry', 'Lovely Cherie', 
        'Superdrug Layering Lab', 'Missoni', 'Perry Ellis', 'Lisboa (by Zara)', 
        'Cyrus Parfums', 'Yes I Am The King', 'Sublime Epoque (Zara)', 
        'Floral Ambrosia (Maison Alhambra sublabel)', 'Le Monde Gourmand', 
        'Manege Rouge', 'Ana Abiyedh Rouge', 'Qasamat Rasasi', 'FA Paris', 
        'Borouj', 'Jeanne en Provence', 'My Perfumes', 'Perfume Parlour', 
        'Signature Night (Armaf)', 'Reha', 'Unique Luxury', 'BBW (Bath & Body Works)', 
        'Coach', 'La Ree Fragrances', 'Szindore', 'Samy Andraus', 'Bint Hooran', 
        'Hamidi', 'Walid Fragrance', 'Albait Aldimashqi', 'Ventana (Armaf)', 
        'Montagne Perfume', 'Alexandre.J'
    ]
    
    # Проверяем существование входного файла
    if not os.path.exists(input_file):
        print(f"Ошибка: файл {input_file} не найден!")
        return
    
    processed_rows = []
    
    # Читаем исходный CSV файл
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            copy_name = row.get('copy_name', '').strip()
            copy_brand = row.get('copy_brand', '').strip()
            
            # Если copy_name не пустое, ищем в нем бренды
            if copy_name:
                found_brand = None
                remaining_name = copy_name
                
                # Ищем бренд в начале copy_name
                for brand in copy_brands:
                    if copy_name.startswith(brand + ' '):
                        found_brand = brand
                        # Убираем найденный бренд из начала строки
                        remaining_name = copy_name[len(brand):].strip()
                        break
                
                # Если нашли бренд в copy_name
                if found_brand:
                    # Если copy_brand пустой, заполняем его
                    if not copy_brand:
                        row['copy_brand'] = found_brand
                    # Обновляем copy_name (убираем бренд)
                    row['copy_name'] = remaining_name
                    
                    print(f"Обработана строка ID {row.get('id', '?')}: "
                          f"'{copy_name}' -> brand: '{found_brand}', name: '{remaining_name}'")
            
            processed_rows.append(row)
    
    # Удаляем дубликаты по copy_name
    print(f"\nИщем дубликаты по copy_name...")
    unique_rows = []
    removed_count = 0
    
    for current_row in processed_rows:
        current_copy_name = current_row.get('copy_name', '').strip()
        
        # Пропускаем строки без copy_name
        if not current_copy_name:
            unique_rows.append(current_row)
            continue
        
        # Ищем похожий copy_name среди уже добавленных
        found_similar = False
        for i, existing_row in enumerate(unique_rows):
            existing_copy_name = existing_row.get('copy_name', '').strip()
            
            if texts_are_similar(current_copy_name, existing_copy_name):
                found_similar = True
                
                # Сравниваем "длину" записей и оставляем лучшую
                current_score = get_text_length_score(current_copy_name)
                existing_score = get_text_length_score(existing_copy_name)
                
                if current_score > existing_score:
                    # Заменяем существующую запись на текущую
                    print(f"Заменяем дубликат: '{existing_copy_name}' -> '{current_copy_name}'")
                    unique_rows[i] = current_row
                else:
                    print(f"Удаляем дубликат: '{current_copy_name}' (оставляем '{existing_copy_name}')")
                
                removed_count += 1
                break
        
        # Если похожих не найдено, добавляем запись
        if not found_similar:
            unique_rows.append(current_row)
    
    # Сортируем данные: сначала по og_brand, и только при одинаковых og_brand - по og_name
    unique_rows.sort(key=lambda x: (
        x.get('og_brand', '').strip().lower(), 
        x.get('og_name', '').strip().lower()
    ))
    
    # Записываем результат в новый файл
    if unique_rows:
        fieldnames = unique_rows[0].keys()
        
        with open(output_file, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unique_rows)
        
        print(f"\n✅ Обработка завершена!")
        print(f"📁 Исходный файл: {input_file}")
        print(f"📁 Новый файл: {output_file}")
        print(f"📊 Всего строк: {len(unique_rows)}")
        print(f"🗑️ Удалено дубликатов: {removed_count}")
        print(f"🔤 Данные отсортированы: сначала по og_brand, при совпадении - по og_name")
    else:
        print("❌ Не удалось обработать данные")

if __name__ == "__main__":
    clean_csv_data()
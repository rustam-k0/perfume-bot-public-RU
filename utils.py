# utils.py

from thefuzz import process

def find_best_match(query, choices):
    """
    Находит наиболее подходящее название из списка.
    
    query: что ввел пользователь (например, "dior savauge")
    choices: список всех парфюмов из БД (например, ["Dior Sauvage", "Chanel No. 5"])
    
    Возвращает лучшее совпадение и его "оценку" схожести (от 0 до 100).
    """
    # extractOne находит одно лучшее совпадение
    best_match = process.extractOne(query, choices)
    
    if best_match:
        # Возвращаем название и оценку
        return best_match[0], best_match[1]
    return None, 0
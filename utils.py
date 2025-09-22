import re
import unicodedata
from thefuzz import fuzz

# Список слов, которые нужно игнорировать при поиске
STOP_WORDS = [
    'парфюм', 'туалетная вода', 'edt', 'edp', 'parfum', 'eau de toilette', 'eau de parfum',
    'de', 'le', 'la', 'l’', 'pour', 'for'
]

# Простая транслитерация (кириллица -> латиница и наоборот)
TRANSLIT_MAP_CYR_TO_LAT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z',
    'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
    'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
}

TRANSLIT_MAP_LAT_TO_CYR = {v: k for k, v in TRANSLIT_MAP_CYR_TO_LAT.items()}

def normalize_query(text: str) -> str:
    """
    Нормализует поисковый запрос:
    - Удаляет лишние пробелы и переводы строк.
    - Переводит в нижний регистр.
    - Удаляет пунктуацию.
    - Удаляет общие слова.
    """
    if not text:
        return ""
    
    # Объединяем множественные пробелы, удаляем пунктуацию и переводим в нижний регистр
    s = re.sub(r'[\s]+', ' ', text).strip().lower()
    s = re.sub(r'[^\w\s]', '', s)
    
    # Удаляем стоп-слова
    s = ' '.join(word for word in s.split() if word not in STOP_WORDS)
    
    # Приводим символы к нормальной форме NFC
    s = unicodedata.normalize('NFC', s)
    
    return s

def transliterate(text: str) -> str:
    """
    Транслитерирует текст: кириллица -> латиница и наоборот.
    Используется для улучшения поиска.
    """
    transliterated_text = ''
    for char in text:
        if char in TRANSLIT_MAP_CYR_TO_LAT:
            transliterated_text += TRANSLIT_MAP_CYR_TO_LAT[char]
        elif char in TRANSLIT_MAP_LAT_TO_CYR:
            transliterated_text += TRANSLIT_MAP_LAT_TO_CYR[char]
        else:
            transliterated_text += char
    return transliterated_text

def find_best_match(query: str, items: list, keys: list) -> tuple:
    """
    Ищет наилучшее совпадение для запроса среди списка объектов.
    Использует нечеткий поиск (fuzzy search) на основе Levenshtein.
    
    Аргументы:
    - query: поисковая строка.
    - items: список словарей/объектов для поиска.
    - keys: список ключей, по которым будет проводиться поиск в каждом объекте.
    
    Возвращает:
    - кортеж (best_match_item, score) или (None, 0).
    """
    normalized_query = normalize_query(query)
    best_match = None
    best_score = 0
    
    for item in items:
        for key in keys:
            if key in item and item[key]:
                item_text = normalize_query(str(item[key]))
                
                # Поиск по точному совпадению
                if item_text == normalized_query:
                    return item, 100
                    
                # Нечеткий поиск
                score = fuzz.ratio(normalized_query, item_text)
                if score > best_score:
                    best_score = score
                    best_match = item
    
    return best_match, best_score
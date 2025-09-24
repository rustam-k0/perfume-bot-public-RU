# perfume-bot/utils.py

import re
import unicodedata

# Словарь для транслитерации ключевых брендов. Можно расширять.
# Словарь для транслитерации ключевых брендов парфюма. Можно расширять.
TRANSLIT_MAP = {
    'заря': 'zara',
    'монталь': 'montale',
    'шанель': 'chanel',
    'диор': 'dior',
    'гуччи': 'gucci',
    'версаче': 'versace',
    'эрмес': 'hermes',
    'пако рабан': 'paco rabanne',
    'иves сен лоран': 'yves saint laurent',
    'том форд': 'tom ford',
    'бонд номер 9': 'bond no.9',
    'лавендерс': 'lavenders',
    'джо мэлоун': 'jo malone',
    'булгари': 'bulgari',
    'фенди': 'fendi',
    'бальмейн': 'balmain',
    'джорджио армани': 'giorgio armani',
    'кельвин кляйн': 'calvin klein',
    'роберто кавалли': 'roberto cavalli',
    'брюно банани': 'bruno banani',
    'эльizabeth арден': 'elizabeth arden',
    'джимми чу': 'jimmy choo',
    'виктор энд ролф': 'viktor & rolf',
    'бискарди': 'biscardi',
    'ла прада': 'prada',
    'марк джейкобс': 'marc jacobs',
    'бальсан': 'balmain',
    'кристиан лакруа': 'christian lacroix',
    'ниссей дэ': 'nissen de',
    'чарльз анжело': 'charles angelo',
    'микель янн': 'michel yann',
    'айвен хью': 'iven hue',
    'флорис': 'floris',
    'амбра': 'ambra',
    'аква ди парама': 'acqua di parma',
    'все парфюмерные дома': 'all perfume houses',
}

# Таблица для посимвольной транслитерации
CHAR_TABLE = {
    "а":"a", "б":"b", "в":"v", "г":"g", "д":"d", "е":"e", "ё":"e", "ж":"zh", 
    "з":"z", "и":"i", "й":"i", "к":"k", "л":"l", "м":"m", "н":"n", "о":"o", 
    "п":"p", "р":"r", "с":"s", "т":"t", "у":"u", "ф":"f", "х":"kh", "ц":"ts", 
    "ч":"ch", "ш":"sh", "щ":"shch", "ъ":"", "ы":"y", "ь":"", "э":"e", "ю":"yu", "я":"ya"
}

def normalize_for_match(s: str) -> str:
    """
    Приводит текст к единому виду для поиска:
    - Приведение к нижнему регистру.
    - Приоритетная транслитерация по словарю (TRANSLIT_MAP).
    - Посимвольная транслитерация для остальных слов.
    - Удаление диакритических знаков (например, в 'Chloé').
    - Удаление всех символов, кроме букв, цифр и пробелов.
    - Нормализация пробелов.
    """
    if not s:
        return ""

    # 1. Приведение к нижнему регистру и нормализация Unicode для удаления диакритики
    s = s.lower()
    s = "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

    # 2. Гибридная транслитерация
    words = s.split()
    translated_words = []
    for word in words:
        # Сначала ищем точное совпадение в словаре
        if word in TRANSLIT_MAP:
            translated_words.append(TRANSLIT_MAP[word])
        else:
            # Если нет, транслитерируем посимвольно
            translated_words.append("".join([CHAR_TABLE.get(char, char) for char in word]))
    
    s = " ".join(translated_words)

    # 3. Удаление всех символов, кроме букв, цифр и пробелов
    s = re.sub(r"[^a-z0-9\s]", "", s)
    
    # 4. Нормализация пробелов (удаление лишних и крайних)
    s = re.sub(r"\s+", " ", s).strip()
    
    return s
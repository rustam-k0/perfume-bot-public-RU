# perfume-bot/i18n.py
# Централизованный словарь для всех локализованных строк.

# --- Настройка языка по умолчанию ---
DEFAULT_LANG = "ru"

MESSAGES = {
    "ru": {
        # web.py / formatter.py (Welcome)
        "welcome": (
            "Привет👋 Я помогу найти доступные **аналоги** дорогого парфюма.\n\n"
            "Отправьте мне сообщение в формате: **Бренд + Название**.\n\n"
            "Например: Dior Sauvage.\n\n"
            "P.S. Я иногда могу растеряться, не сердитесь. 🥺"
        ),
        
        # search.py (Errors)
        "error_empty_query": "Ой, я ничего не получил. Отправьте мне **бренд и название аромата**, пожалуйста.",
        "error_brand_only": "Кажется, вы не указали название целиком. Я нашёл бренд **{brand_name}**. Пожалуйста, введите и название парфюма тоже.",
        "error_not_found": "Увы, этот аромат пока мне не знаком. 😅 Пожалуйста, проверьте, правильно ли указаны бренд и название, или попробуйте другой.",
        
        # search.py / web.py (Notes/Warnings)
        "note_fuzzy_match": "Найдено по неточному совпадению. Проверьте результат.",
        
        # followup.py
        "followup_text": "Круто! 🎉 Кажется, поиск сработал. Может, попробуем найти ещё один аромат?",
        
        # formatter.py (Response body)
        "response_not_found_copies": (
            "Мне не удалось найти подходящие аналоги. Попробуйте ввести данные целиком (**Бренд + Название**) или поищите другой аромат. 😣"
        ),
        "response_search_link_prefix": "купить", # Часть ссылки [купить]
        "response_close": "Надеюсь, информация была полезной! ✨ Готовы попробовать еще раз?",
        "response_note_prefix": "**🤖 Внимание:** "
    },
    
    "en": {
        # web.py / formatter.py (Welcome)
        "welcome": (
            "Hey there! 👋 I can help you find affordable **dupes** for expensive perfumes.\n\n"
            "Send me a message in the format: **Brand + Name**.\n\n"
            "For example: Dior Sauvage.\n\n"
            "P.S. I sometimes get confused, so please be patient! 🥺"
        ),
        
        # search.py (Errors)
        "error_empty_query": "Oops, I didn't get anything. Please send me the **brand and name of the fragrance**.",
        "error_brand_only": "It looks like you didn't include the full name. I found the brand **{brand_name}**. Please enter the perfume's name as well.",
        "error_not_found": "Sorry, I don't know this fragrance yet. 😅 Please check that the brand and name are spelled correctly, or try another one.",
        
        # search.py / web.py (Notes/Warnings)
        "note_fuzzy_match": "Found via fuzzy match. Please check the result.",
        
        # followup.py
        "followup_text": "Awesome! 🎉 It seems the search worked. Ready to try finding another perfume?",
        
        # formatter.py (Response body)
        "response_not_found_copies": (
            "I couldn't find any suitable dupes. Try entering the full details (**Brand + Name**) or search for a different fragrance. 😣"
        ),
        "response_search_link_prefix": "buy", # Часть ссылки [buy]
        "response_close": "Hope the info was helpful! ✨ Wanna try again?",
        "response_note_prefix": "**🤖 Attention:** "
    }
}

def get_message(key: str, lang: str = DEFAULT_LANG):
    """Извлекает локализованную строку, используя язык и ключ."""
    lang = lang.lower()
    # Fallback на язык по умолчанию, если указанный язык не найден
    if lang not in MESSAGES:
        lang = DEFAULT_LANG
    
    # Возвращаем сообщение или плейсхолдер ошибки
    return MESSAGES[lang].get(key, f"MISSING_STRING_KEY_{key}")
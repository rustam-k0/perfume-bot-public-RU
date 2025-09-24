# perfume-bot/formatter.py
# Форматирование текста ответов.

import urllib.parse

def welcome_text():
    return (
        "Привет👋 \n\n"
        "Я ищу доступные аналоги дорогого парфюма.\n\n"
        "Отправьте сообщение в формате: БРЕНД + НАЗВАНИЕ.\n\n"
        "Например: Dior Sauvage.\n\n"
        "P.S.Иногда я могу растеряться. Пожалуйста, не сердитесь.🥺\n\n"
    )

def create_search_link(brand, name):
    """
    Создает URL для поиска Google по заданным бренду и названию.
    """
    query = f"купить {brand} {name} онлайн"
    encoded_query = urllib.parse.quote_plus(query)
    return f"https://www.google.com/search?q={encoded_query}"

def format_response(original, copies):
    lines = []
    
    # Форматируем оригинал
    original_link = create_search_link(original['brand'], original['name'])
    
    original_brand = original['brand'] if original['brand'] else ''
    original_name = original['name'] if original['name'] else ''
    
    lines.append(f"**{original_brand} {original_name}** [купить]({original_link})")
    lines.append("---------------------")

    if not copies:
        lines.append("Мне не удалось найти этот аромат."
                     "Скорее всего, я не знаком с ним или мне не хвататет данных для поиска.\n\n"
                     "Может быть, попробуете написать бренд и название целиком? Или другой аромат?😣 \n\n")
    else:
        for c in copies:
            brand = c["brand"] if c["brand"] else ""
            name = c["name"] if c["name"] else ""
            copy_link = create_search_link(brand, name)
            
            # Условное форматирование для вывода названия и бренда
            if brand and name:
                lines.append(f"▪️ {brand}: {name} [купить]({copy_link})")
            elif name:
                lines.append(f"▪️ {name} [купить]({copy_link})")
            elif brand:
                lines.append(f"▪️ {brand} [купить]({copy_link})")
            
    lines.append("---------------------")
    lines.append("Отлично!")
    lines.append("Надеюсь, я правильно вас понял. Хотите попробовать ещё?")
    
    return "\n".join(lines)
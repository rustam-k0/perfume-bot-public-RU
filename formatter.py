# perfume-bot/formatter.py
# Форматирование текста ответов.

import urllib.parse

def welcome_text():
    return (
        "Привет! 👋 Я помогу найти доступный аналог для вашего любимого парфюма.\n\n"
        "Как правило, себестоимость дорого парфюма меньше 10%. А отальное - это маркетинг, упаковка и доставка."
        "Хорошая новость: мы собрали базу из лучших клонов. Они пахнут так же, как оригинал - за крошечную долю цены.\n\n"
        "Попробуйте отправить название оригинала в формате: «Бренд Название», например: Dior Sauvage."
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
        lines.append("К сожалению, для этого аромата не удалось найти клонов. 😅")
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
    lines.append("У вас отлично получилось!")
    lines.append("Советую поискать эти ароматы в любимой парфюмерной сети или на маркетплейсе.")
    
    return "\n".join(lines)
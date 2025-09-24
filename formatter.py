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
    
    # Форматируем оригинал с гиперссылкой в одной строке
    original_link = create_search_link(original['brand'], original['name'])
    lines.append(f"**{original['brand']} {original['name']}** ([купить]({original_link}))")
    lines.append("---------------------")

    if not copies:
        lines.append("К сожалению, для этого аромата не удалось найти клонов. 😅")
    else:
        for c in copies:
            brand, name = c["brand"], c["name"]
            copy_link = create_search_link(brand, name)
            
            lines.append(f"▪️ {brand}: {name} ([купить]({copy_link}))")
            
    lines.append("---------------------")
    lines.append("У вас отлично получилось!")
    lines.append("Советую поискать эти ароматы в любимой парфюмерной сети или на маркетплейсе.")
    
    return "\n".join(lines)
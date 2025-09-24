# perfume-bot/formatter.py
# Форматирование текста ответов.

import urllib.parse
import re

def welcome_text():
    return (
        "Привет\\! 👋 Я помогу найти доступный аналог для вашего любимого парфюма\\.\n\n"
        "Как правило, себестоимость дорого парфюма меньше 10\\%\\.\n"
        "Хорошая новость\\: мы собрали базу из лучших клонов\\. Они пахнут так же, как оригинал \\- за крошечную долю цены\\.\n\n"
        "Попробуйте отправить название оригинала в формате\\: «Бренд Название», например\\: Dior Sauvage\\."
    )

def escape_markdown_v2(text):
    """
    Экранирует специальные символы MarkdownV2.
    """
    # Список символов, которые нужно экранировать
    # Отметьте, что `.` также экранируется для корректного отображения цен
    special_chars = r"([_*`\[\]()~>#+=|{}.!-])"
    return re.sub(special_chars, r'\\\1', text)


def create_search_link(brand, name):
    """
    Создает URL для поиска Google по заданным бренду и названию.
    """
    query = f"купить {brand} {name} онлайн"
    encoded_query = urllib.parse.quote_plus(query)
    return f"https://www.google.com/search?q={encoded_query}"


def format_response(original, copies):
    lines = []
    
    # Экранируем название оригинала
    original_brand = escape_markdown_v2(original['brand'])
    original_name = escape_markdown_v2(original['name'])
    original_link = create_search_link(original['brand'], original['name'])
    
    lines.append(f"*{original_brand} {original_name}*")
    lines.append(f"🛒 [Купить оригинал]({original_link})")
    
    lines.append("---------------------")

    if not copies:
        lines.append("К сожалению, для этого аромата не удалось найти клонов\\. 😅")
    else:
        for c in copies:
            brand, name = escape_markdown_v2(c["brand"]), escape_markdown_v2(c["name"])
            copy_link = create_search_link(c['brand'], c['name'])
            
            lines.append(f"▪️ {brand}\\: {name}")
            lines.append(f"🛒 [Купить клон]({copy_link})")
            
    lines.append("---------------------")
    lines.append("У вас отлично получилось\\!")
    lines.append("Советую поискать эти ароматы в любимой парфюмерной сети или на маркетплейсе\\.")
    
    return "\n".join(lines)
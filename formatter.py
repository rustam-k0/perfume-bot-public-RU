# perfume-bot/formatter.py
# Форматирование текста ответов с учетом контекста поиска.

import urllib.parse

def welcome_text():
    """Сохраняем исходное приветственное сообщение."""
    return (
        "Привет! 👋 Я помогу найти доступный аналог для вашего любимого парфюма.\n\n"
        "Как правило, себестоимость дорого парфюма меньше 10%. А отальное - это маркетинг, упаковка и доставка."
        "Хорошая новость: мы собрали базу из лучших клонов. Они пахнут так же, как оригинал - за крошечную долю цены.\n\n"
        "Попробуйте отправить название оригинала в формате: «Бренд Название», например: Dior Sauvage."
    )

def create_search_link(brand, name):
    """Создает URL для поиска Google."""
    query = f"купить {brand} {name} онлайн"
    encoded_query = urllib.parse.quote_plus(query)
    return f"https://www.google.com/search?q={encoded_query}"

def format_perfume_info(search_result, copies):
    """
    Формирует красивый текст ответа на основе результатов поиска.
    Принимает словарь от find_original и список клонов.
    """
    if not search_result.get("ok"):
        return search_result.get("message", "Произошла неизвестная ошибка.")

    original = search_result.get("original")
    match_type = search_result.get("match_type")
    
    # 1. Формируем заголовок в зависимости от типа совпадения
    original_brand = original.get('brand', '')
    original_name = original.get('name', '')
    original_link = create_search_link(original_brand, original_name)
    
    header = {
        "exact": f"Отлично! Я нашел оригинал:\n*{original_brand} {original_name}* [купить]({original_link})",
        "clone": f"Вы искали клон? Я нашел его оригинал:\n*{original_brand} {original_name}* [купить]({original_link})",
        "fuzzy": f"Возможно, вы имели в виду:\n*{original_brand} {original_name}* [купить]({original_link})",
    }.get(match_type, f"Вот что я нашел:\n*{original_brand} {original_name}* [купить]({original_link})")

    lines = [header, "---"]
    
    # 2. Формируем информацию о клонах
    if not copies:
        lines.append("К сожалению, для этого аромата пока не найдено аналогов. 😔")
    else:
        lines.append("✅ *Доступные аналоги:*")
        for copy in copies:
            brand, name = copy.get("brand", ""), copy.get("name", "")
            copy_link = create_search_link(brand, name)
            # Экономия, если она есть в данных
            savings = f" (экономия {int(copy['saved_amount'])}%)" if 'saved_amount' in copy else ""
            lines.append(f"▪️ *{brand}* – {name}{savings} [купить]({copy_link})")
            
    lines.append("---")
    lines.append("Надеюсь, это поможет вам сэкономить! 😉")
    
    return "\n".join(lines)
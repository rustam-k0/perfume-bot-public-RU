# perfume-bot/formatter.py
# Форматирование текста ответов.

def welcome_text():
    return (
        "Привет! 👋 Я помогу найти доступный аналог для вашего любимого парфюма.\n\n"
        "Как правило, себестоимость дорого парфюма меньше 10%. А отальное - это маркетинг, упаковка и доставка."
        "Хорошая новость: мы собрали базу из лучших клонов. Они пахнут так же, как оригинал - за крошечную долю цены.\n\n"
        "Попробуйте отправить название оригинала в формате: «Бренд Название», например: Dior Sauvage."
    )

def format_response(original, copies):
    lines = []
    header = f"{original['brand']} {original['name']}".strip()
    if header:
        lines.append(header)
    lines.append("---------------------")
    
    

    if not copies:
        lines.append("Не получилось найти то, что вы искали. Пожалуйста, попробуйте снова. 😅")
    else:
        for c in copies:
            brand, name = c["brand"], c["name"]
            if brand and name:
                lines.append(f"▪️ {brand}: {name}")
            elif name:
                lines.append(f"▪️ {name}")
            elif brand:
                lines.append(f"▪️ {brand}")

    lines.append("---------------------")
    lines.append("У вас отлично получилось!")
    lines.append("Советую поискать эти ароматы в  любимой парфюмерной сети или на маркетплейсе.")
    return "\n".join(lines)


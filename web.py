# perfume-bot/web.py

import os
import time
from flask import Flask, request
import telebot
from dotenv import load_dotenv

# Обновляем импорты для соответствия новой логике
from database import connect_db, fetch_clones_by_original_id
from search import find_original, init_catalog  # Добавляем init_catalog
from formatter import format_perfume_info, welcome_text # Меняем format_response на format_perfume_info
from followup import schedule_followup_once

# --- Загружаем переменные окружения ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", "data/perfumes.db")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не указан в .env!")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL не указан в .env!")

# --- Инициализация ---
bot = telebot.TeleBot(BOT_TOKEN)
# Используем консистентное имя функции для подключения
conn = connect_db(DB_PATH) 

# (!) ВАЖНО: Инициализируем каталог поиска один раз при запуске приложения
init_catalog(conn)
print("Каталог парфюмов загружен в память для быстрого поиска.")

last_user_ts = {}
followup_sent = {}



# ... (все ваши импорты и начальный код остаются без изменений) ...

@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_text(msg):
    """
    Основной обработчик с логированием ошибок для отладки.
    """
    chat_id = msg.chat.id
    now = time.time()
    last_user_ts[chat_id] = now
    
    try:
        # 1. Вызываем основную функцию поиска
        print(f"Поиск по запросу: '{msg.text}'") # Добавим лог для отладки
        search_result = find_original(conn, msg.text)
        print(f"Результат поиска: {search_result}") # Посмотрим, что вернул поиск

        # 2. Если поиск успешен, получаем клоны и форматируем ответ
        if search_result.get("ok"):
            original = search_result.get("original")
            
            # Проверка, что 'original' не пустой, перед тем как искать id
            if not original:
                raise ValueError("Функция поиска вернула ok:True, но 'original' пустой.")

            original_id = original.get("id")
            copies = fetch_clones_by_original_id(conn, original_id)
            
            response_text = format_perfume_info(search_result, copies)
        else:
            # Если поиск не дал результатов, просто возвращаем сообщение
            response_text = search_result.get("message")
        
        # 3. Отправляем итоговое сообщение пользователю
        bot.send_message(
            chat_id, 
            response_text, 
            parse_mode='Markdown', 
            disable_web_page_preview=True
        )

        # Логика для отложенного сообщения
        if search_result.get("ok"):
            schedule_followup_once(bot, chat_id, now, last_user_ts, followup_sent)

    except Exception as e:
        # !!! ЭТО САМАЯ ВАЖНАЯ ЧАСТЬ !!!
        # Если внутри try что-то сломается, мы увидим ошибку в консоли
        print(f"💥💥💥 Произошла критическая ошибка: {e} 💥💥💥")
        # И сообщим пользователю, что что-то пошло не так
        bot.send_message(
            chat_id,
            "Ой, что-то пошло не так на сервере. 😵‍💫 Уже разбираюсь!"
        )

# ... (остальной код web.py остается без изменений) ...

# --- Flask веб-сервер ---
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Perfume Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "", 200

# --- Запуск ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("Запуск бота через вебхук...")
    bot.remove_webhook()
    time.sleep(0.5) # Пауза перед установкой нового вебхука
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=port)
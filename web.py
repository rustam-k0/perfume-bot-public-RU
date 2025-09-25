# perfume-bot/web.py (Улучшенная версия)
import os
import time
from flask import Flask, request
import telebot
from dotenv import load_dotenv
import traceback

from database import get_connection, get_copies_by_original_id, log_message, init_db_if_not_exists
# !!! Добавляем импорт init_catalog для явного вызова !!!
from search import find_original, init_catalog 
from formatter import format_response, welcome_text
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

# --- Инициализация бота и базы данных ---
bot = telebot.TeleBot(BOT_TOKEN)
conn = get_connection(DB_PATH)

# ГАРАНТИРУЕМ ИНИЦИАЛИЗАЦИЮ ТАБЛИЦ (ВКЛЮЧАЯ UserMessages)
init_db_if_not_exists(conn)

# ГАРАНТИРУЕМ ИНИЦИАЛИЗАЦИЮ КАТАЛОГА С ОБРАБОТКОЙ ОШИБОК
try:
    init_catalog(conn)
    print("✅ Каталог парфюмов успешно загружен в память.")
except Exception as e:
    print(f"❌ Критическая ошибка при загрузке каталога: {e}")
    # Не поднимаем ошибку, чтобы дать боту возможность работать (хотя бы логировать)
    # При пустом каталоге все поисковые запросы будут 'fail'
    
last_user_ts = {}
followup_sent = {}

# --- Обработчики ---
@bot.message_handler(commands=["start", "help"])
def start(msg):
    # Логирование команды 'start'
    log_message(conn, msg.chat.id, msg.text, 'start_command', "User started or requested help.")
    bot.reply_to(msg, welcome_text())

@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_text(msg):
    chat_id = msg.chat.id
    query_text = msg.text
    now = time.time()
    last_user_ts[chat_id] = now
    
    # 1. Инициализация переменных для гарантированного логирования в блоке finally
    log_status = 'fail'
    log_notes = "Unknown error before processing started"
    
    try:
        result = find_original(conn, query_text)
        
        if not result["ok"]:
            # Случай 1: Поиск не дал результатов (штатная неудача)
            log_notes = result['message']
            bot.reply_to(msg, result["message"])
            return 
        
        # Поиск успешен. Начинается потенциально проблемный блок (DB/форматирование)
        original = result["original"]
        copies = get_copies_by_original_id(conn, original["id"]) 
        
        response_text = format_response(original, copies) 
        
        # Случай 2: Все успешно
        log_status = 'success'
        log_notes = f"Found: {original['brand']} {original['name']}"
        
        bot.reply_to(msg, response_text, parse_mode='Markdown', disable_web_page_preview=True)

        schedule_followup_once(bot, chat_id, now, last_user_ts, followup_sent)

    except Exception as e:
        # Случай 3: Непредвиденная ошибка
        log_notes = f"Critical handler error: {type(e).__name__}: {str(e)}"
        log_status = 'fail' 
        bot.reply_to(msg, "Произошла критическая ошибка. Пожалуйста, попробуйте позже.")
        
    finally:
        # 4. ГАРАНТИРОВАННОЕ ЛОГИРОВАНИЕ: Выполняется в любом случае
        log_message(conn, chat_id, query_text, log_status, log_notes)

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
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=port)
# perfume-bot/web.py
import os # Этот модуль уже импортирован
import time
from flask import Flask, request
import telebot
from dotenv import load_dotenv

from database import get_connection, get_copies_by_original_id, log_message, init_db_if_not_exists
from search import find_original
from formatter import format_response, welcome_text
from followup import schedule_followup_once

# --- Загружаем переменные окружения ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ОПТИМИЗАЦИЯ: Использование абсолютного пути для DB_PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Если DB_PATH не указан в .env, он будет собран абсолютно: BASE_DIR/data/perfumes.db
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "data", "perfumes.db"))

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не указан в .env!")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL не указан в .env!")

# --- Инициализация бота и базы данных ---
bot = telebot.TeleBot(BOT_TOKEN)
conn = get_connection(DB_PATH) # Использует теперь гарантированно правильный путь
init_db_if_not_exists(conn)

last_user_ts = {}
followup_sent = {}

# --- Обработчики (логика обработки текста обновлена для 'note' из search.py) ---
@bot.message_handler(commands=["start", "help"])
def start(msg):
    log_message(conn, msg.chat.id, msg.text, 'start_command')
    bot.reply_to(msg, welcome_text())

@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_text(msg):
    chat_id = msg.chat.id
    now = time.time()
    last_user_ts[chat_id] = now

    result = find_original(conn, msg.text)
    
    # 1. Обработка неуспешного поиска (включая неполный запрос по бренду)
    if not result["ok"]:
        log_message(conn, msg.chat.id, msg.text, 'fail', result['message'])
        bot.reply_to(msg, result["message"])
        return

    # 2. Обработка успешного поиска
    original = result["original"]
    copies = get_copies_by_original_id(conn, original["id"])
    
    # Сборка заметки для лога. Включаем 'note' из search.py, если он есть.
    log_note = f"Found: {original['brand']} {original['name']}"
    if 'note' in result:
        # Добавляем информацию о фаззи-совпадении в лог
        log_note += f" | NOTE: {result['note']}" 
        
    log_message(conn, msg.chat.id, msg.text, 'success', log_note)
    
    # Формируем ответ, включая потенциальную заметку о неточном поиске
    response_text = format_response(original, copies)
    if 'note' in result:
        # Добавляем предупреждение о неточном поиске перед результатом
        response_text = f"**🤖 Внимание:** {result['note']} \n\n" + response_text 
        
    bot.reply_to(msg, response_text, parse_mode='Markdown', disable_web_page_preview=True)

    schedule_followup_once(bot, chat_id, now, last_user_ts, followup_sent)

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
# perfume-bot/web.py (упрощённая версия)
import os
import time
from flask import Flask, request
import telebot
from dotenv import load_dotenv

from database import get_connection, get_copies_by_original_id, log_message, init_db_if_not_exists
from search import find_original, init_catalog
from formatter import format_response, welcome_text
from followup import schedule_followup_once

# --- Настройка окружения ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", "data/perfumes.db")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN or not WEBHOOK_URL:
    raise ValueError("BOT_TOKEN и WEBHOOK_URL должны быть заданы в .env")

# --- Инициализация ---
bot = telebot.TeleBot(BOT_TOKEN)
conn = get_connection(DB_PATH)
init_db_if_not_exists(conn)

try:
    init_catalog(conn)
    print("✅ Каталог парфюмов загружен.")
except Exception as e:
    print(f"❌ Ошибка загрузки каталога: {e}")

last_user_ts = {}
followup_sent = {}

# --- Обработчики ---
@bot.message_handler(commands=["start", "help"])
def start(msg):
    log_message(conn, msg.chat.id, msg.text, "start_command", "Start/help")
    bot.reply_to(msg, welcome_text())

@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_text(msg):
    chat_id, query_text, now = msg.chat.id, msg.text, time.time()
    last_user_ts[chat_id] = now
    status, notes = "fail", "Unhandled error"

    try:
        result = find_original(conn, query_text)

        if not result["ok"]:
            notes = result["message"]
            bot.reply_to(msg, notes)
            return

        original = result["original"]
        copies = get_copies_by_original_id(conn, original["id"])
        response = format_response(original, copies)

        status, notes = "success", f"Found: {original['brand']} {original['name']}"
        bot.reply_to(msg, response, parse_mode="Markdown", disable_web_page_preview=True)
        schedule_followup_once(bot, chat_id, now, last_user_ts, followup_sent)

    except Exception as e:
        notes = f"Critical: {type(e).__name__}: {e}"
        bot.reply_to(msg, "Произошла критическая ошибка. Попробуйте позже.")
    finally:
        log_message(conn, chat_id, query_text, status, notes)

# --- Flask ---
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Perfume Bot is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return "", 200

# --- Запуск ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=port)

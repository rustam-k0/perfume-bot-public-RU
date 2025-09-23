import os
import time
from flask import Flask, request
import telebot
from dotenv import load_dotenv

from database import get_connection, get_copies_by_original_id
from search import find_original
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

last_user_ts = {}
followup_sent = {}

# --- Обработчики ---
@bot.message_handler(commands=["start", "help"])
def start(msg):
    bot.reply_to(msg, welcome_text())

@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_text(msg):
    chat_id = msg.chat.id
    now = time.time()
    last_user_ts[chat_id] = now

    result = find_original(conn, msg.text)
    if not result["ok"]:
        bot.reply_to(msg, result["message"])
        return

    original = result["original"]
    copies = get_copies_by_original_id(conn, original["id"])
    bot.reply_to(msg, format_response(original, copies))

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

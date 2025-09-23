import os
from flask import Flask, request
import telebot
from dotenv import load_dotenv

from database import get_connection, get_copies_by_original_id
from search import find_original
from formatter import format_response, welcome_text
from followup import schedule_followup_once

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", "data/perfumes.db")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env. Добавьте токен бота.")

bot = telebot.TeleBot(BOT_TOKEN)
conn = get_connection(DB_PATH)

last_user_ts = {}
followup_sent = {}

# Обработчики
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

# Flask веб-сервер для Render
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    bot.remove_webhook()
    # Укажи сюда свой публичный URL Render
    bot.set_webhook(url=f"https://<твое-доменное-имя>.onrender.com/webhook")
    app.run(host="0.0.0.0", port=port)

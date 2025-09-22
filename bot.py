
# perfume-bot/bot.py
# Главный файл: запускает Telegram-бота, обрабатывает сообщения и отвечает.

import os
import time
from dotenv import load_dotenv
import telebot

from database import get_connection, get_copies_by_original_id
from search import find_original
from formatter import format_response, welcome_text
from followup import schedule_followup_once

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")  # токен Telegram-бота
DB_PATH = os.getenv("DB_PATH", "data/perfumes.db")  # путь к базе данных

# Проверка токена
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env. Добавьте токен бота.")

# Создаем объект TeleBot
bot = telebot.TeleBot(BOT_TOKEN)

# Подключение к базе данных
conn = get_connection(DB_PATH)

# Словари для отслеживания последнего сообщения пользователя и follow-up
last_user_ts = {}
followup_sent = {}

# Команда /start или /help — приветствие
@bot.message_handler(commands=["start", "help"])
def start(msg):
    bot.reply_to(msg, welcome_text())

# Обработка любого текстового сообщения
@bot.message_handler(func=lambda m: True, content_types=["text"])
def handle_text(msg):
    chat_id = msg.chat.id
    now = time.time()
    last_user_ts[chat_id] = now

    # Поиск оригинального парфюма
    result = find_original(conn, msg.text)

    if not result["ok"]:
        # Не нашли — просим уточнить
        bot.reply_to(msg, result["message"])
        return

    original = result["original"]
    # Получаем все доступные клоны
    copies = get_copies_by_original_id(conn, original["id"])

    # Формируем красивый ответ и отправляем
    bot.reply_to(msg, format_response(original, copies))

    # Планируем follow-up через 30 секунд (отправится 1 раз)
    schedule_followup_once(bot, chat_id, now, last_user_ts, followup_sent)

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен — готов принимать сообщения.")
    try:
        # Запуск постоянного прослушивания сообщений
        bot.infinity_polling(timeout=60, long_polling_timeout=5)
    except Exception as e:
        print("Ошибка при запуске бота:", e)
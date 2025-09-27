# perfume-bot/web.py
import os
import time
from flask import Flask, request
import telebot
from telebot import types 
from dotenv import load_dotenv

from database import get_connection, get_copies_by_original_id, log_message, init_db_if_not_exists
from search import find_original
from formatter import format_response, welcome_text
from followup import schedule_followup_once
from i18n import DEFAULT_LANG, get_message

# --- Загружаем переменные окружения ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ОПТИМИЗАЦИЯ: Использование абсолютного пути для DB_PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "data", "perfumes.db"))

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не указан в .env!")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL не указан в .env!")

# --- Инициализация бота и базы данных ---
bot = telebot.TeleBot(BOT_TOKEN)
conn = get_connection(DB_PATH) 
init_db_if_not_exists(conn)

last_user_ts = {}
followup_sent = {}


# --- Вспомогательная функция для создания кнопок языка ---
def get_language_keyboard(lang=DEFAULT_LANG):
    """Создает Inline-клавиатуру для выбора языка."""
    markup = types.InlineKeyboardMarkup()
    # Кнопка для русского языка
    ru_button = types.InlineKeyboardButton(
        get_message("button_lang_ru", lang), 
        callback_data="lang:ru"
    )
    # Кнопка для английского языка
    en_button = types.InlineKeyboardButton(
        get_message("button_lang_en", lang), 
        callback_data="lang:en"
    )
    markup.add(en_button, ru_button)
    return markup


# --- Хендлер команды /start и /help (с языком по умолчанию 'ru') ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(msg):
    chat_id = msg.chat.id
    lang = DEFAULT_LANG 
    
    log_message(conn, chat_id, msg.text, 'start_command')
    
    welcome_msg = welcome_text(lang=lang)
    
    bot.send_message(
        chat_id, 
        welcome_msg, 
        parse_mode='Markdown', # <-- ДОБАВЛЕНО/ИСПРАВЛЕНО ДЛЯ ФОРМАТИРОВАНИЯ
        reply_markup=get_language_keyboard(lang)
    )


# --- НОВЫЙ Хендлер для обработки нажатия Inline-кнопки ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('lang:'))
def callback_inline_language(call):
    chat_id = call.message.chat.id
    new_lang = call.data.split(':')[1]
    
    welcome_msg = welcome_text(lang=new_lang)
    
    try:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=welcome_msg,
            parse_mode='Markdown' # <-- ДОБАВЛЕНО/ИСПРАВЛЕНО ДЛЯ ФОРМАТИРОВАНИЯ
        )
    except Exception as e:
        print(f"Error editing message: {e}")
        bot.send_message(chat_id, welcome_msg, parse_mode='Markdown') # <-- ДОБАВЛЕНО/ИСПРАВЛЕНО ДЛЯ ФОРМАТИРОВАНИЯ
        
    confirm_msg = get_message("confirm_lang_set", new_lang)
    bot.answer_callback_query(call.id, text=confirm_msg)


# --- Хендлер текстовых сообщений ---
@bot.message_handler(func=lambda msg: True)
def handle_message(msg):
    chat_id = msg.chat.id
    user_text = msg.text.strip()
    now = int(time.time())
    
    lang = DEFAULT_LANG 
    
    last_user_ts[chat_id] = now
    followup_sent[chat_id] = False
    
    if not user_text:
        error_msg = get_message("error_empty_query", lang)
        log_message(conn, msg.chat.id, msg.text, 'fail', 'Empty query')
        bot.reply_to(msg, error_msg, parse_mode='Markdown') # <-- ДОБАВЛЕНО/ИСПРАВЛЕНО ДЛЯ ФОРМАТИРОВАНИЯ
        return

    result = find_original(conn, user_text, lang=lang) 

    if not result["ok"]:
        log_message(conn, msg.chat.id, msg.text, 'fail', result['message'])
        bot.reply_to(msg, result['message'], parse_mode='Markdown') # <-- ДОБАВЛЕНО/ИСПРАВЛЕНО ДЛЯ ФОРМАТИРОВАНИЯ
        return

    original = result["original"]
    copies = get_copies_by_original_id(conn, original["id"])
    
    log_note = f"Found: {original['brand']} {original['name']}"
    if 'note' in result:
        log_note += f" | NOTE: {result['note']}" 
        
    log_message(conn, msg.chat.id, msg.text, 'success', log_note)
    
    response_text = format_response(original, copies, lang=lang)
    
    if 'note' in result:
        note_prefix = get_message("response_note_prefix", lang)
        response_text = f"{note_prefix}{result['note']} \n\n" + response_text 
        
    bot.reply_to(msg, 
                 response_text, 
                 parse_mode='Markdown', # <-- ДОБАВЛЕНО/ИСПРАВЛЕНО ДЛЯ ФОРМАТИРОВАНИЯ
                 disable_web_page_preview=True)

    schedule_followup_once(bot, chat_id, now, last_user_ts, followup_sent, lang=lang)

# --- Flask веб-сервер ---
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    # Используем DEFAULT_LANG из i18n.py
    return f"Perfume Bot is running! Default lang: {DEFAULT_LANG}"

@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == '__main__':
    print(f"Starting bot with default language: {DEFAULT_LANG}")
    # --- 🌟 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ ДЕПЛОЯ НА RENDER 🌟 ---
    # Получаем порт из переменной окружения, устанавливаемой Render (по умолчанию 5000)
    port = int(os.getenv("PORT", 5000))
    # Запускаем Flask-сервер, прослушивая все внешние интерфейсы ('0.0.0.0')
    app.run(host='0.0.0.0', port=port)
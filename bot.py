# bot.py

import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import database
import utils

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение при команде /start."""
    await update.message.reply_text(
        '👋 Привет! Я парфюмерный бот.\n'
        'Отправь мне название парфюма, и я найду его и популярные клоны.'
    )

async def search_perfume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает текстовые сообщения для поиска парфюма."""
    user_query = update.message.text
    all_perfumes = database.get_all_original_perfumes()
    best_match, score = utils.find_best_match(user_query, all_perfumes)
    
    if score > 70:
        original, clones = database.find_perfume_and_clones(best_match)
        
        if original:
            # --- Формируем ответ, проверяя каждое поле ---
            response = f"🌟 **Оригинал:** {original['brand']} {original['name']}\n"
            
            ### ИЗМЕНЕНО: Показываем цену и ссылку, только если они есть ###
            if original['price_eur'] is not None:
                response += f"💰 *Цена:* {original['price_eur']:.2f} €\n"
            if original['url']:
                response += f"🔗 [Ссылка]({original['url']})\n"
            
            response += "\n"

            # Фильтруем клоны, у которых есть и бренд, и название
            valid_clones = [c for c in clones if c['brand'] and c['name']]

            if valid_clones:
                response += "👯 **Найденные клоны:**\n"
                response += "---------------------\n"
                for clone in valid_clones:
                    response += f"🔸 **{clone['brand']} {clone['name']}**\n"
                    
                    ### ИЗМЕНЕНО: Показываем цену клона, только если она есть ###
                    if clone['price_eur'] is not None:
                        response += f"💰 *Цена:* {clone['price_eur']:.2f} €\n"

                    ### ИЗМЕНЕНО: Считаем и показываем экономию, только если ОБЕ цены существуют ###
                    if original['price_eur'] is not None and clone['price_eur'] is not None:
                        # Проверяем, что цена оригинала больше нуля, чтобы избежать деления на ноль
                        if original['price_eur'] > 0:
                            saving = (original['price_eur'] - clone['price_eur']) / original['price_eur'] * 100
                            response += f"💸 *Экономия:* **{saving:.0f}%**\n"
                    
                    ### ИЗМЕНЕНО: Показываем ссылку на клон, только если она есть ###
                    if clone['url']:
                         response += f"🔗 [Ссылка]({clone['url']})\n"
                    
                    response += "\n" # Добавляем отступ после каждого клона
            else:
                response += "😔 Клонов для этого парфюма пока не найдено."
        
            await update.message.reply_text(response, parse_mode='Markdown', disable_web_page_preview=True)
        
    else:
        await update.message.reply_text("😕 Не смог найти такой парфюм. Попробуйте написать иначе.")


def main():
    """Запускает бота."""
    print("Бот запускается...")
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_perfume))
    application.run_polling()

if __name__ == '__main__':
    main()
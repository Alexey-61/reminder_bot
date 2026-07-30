import sys
import os

# Добавляем путь к папке reminder_bot (если есть)
sys.path.append(os.path.join(os.path.dirname(__file__), 'reminder_bot'))

import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database.db import Database
from handlers import start, create, list, settings, callback
from keyboards.keyboards import get_reminder_actions_keyboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# Регистрация роутеров
dp.include_router(start.router)
dp.include_router(create.router)
dp.include_router(list.router)
dp.include_router(settings.router)
dp.include_router(callback.router)

db = Database()

def check_reminders():
    """Проверяет напоминания и отправляет их"""
    try:
        due = db.get_due_reminders()
        for rem in due:
            kb = get_reminder_actions_keyboard(rem['id'])
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                bot.send_message(
                    rem['user_id'],
                    f"🔔 **Напоминание!**\n\n{rem['text']}",
                    reply_markup=kb
                )
            )
            loop.close()
            if rem['reminder_type'] == 'once':
                db.disable_reminder(rem['id'])
    except Exception as e:
        logger.error(f"Ошибка проверки: {e}")

def background_worker():
    """Фоновый поток для проверки напоминаний"""
    logger.info("🔄 Фоновый поток запущен")
    while True:
        try:
            check_reminders()
        except Exception as e:
            logger.error(f"Ошибка в фоновом потоке: {e}")
        time.sleep(30)

# Запускаем фоновый поток
thread = threading.Thread(target=background_worker, daemon=True)
thread.start()

# ============ ВЕБХУК ============
@app.route("/webhook", methods=['POST'])
async def webhook():
    """Точка входа для вебхуков от Telegram"""
    try:
        # Получаем данные от Telegram
        data = await request.get_json()
        
        # Проверяем, что данные пришли
        if not data:
            logger.warning("Пустой запрос от Telegram")
            return "OK", 200
        
        logger.info(f"📨 Получен вебхук: {data.get('message', {}).get('text', 'не текст')}")
        
        # Преобразуем в объект Update
        update = Update.model_validate(data, context={"bot": bot})
        
        # Передаём в диспетчер
        await dp.feed_update(bot, update)
        
        return "OK", 200
    except Exception as e:
        logger.error(f"❌ Ошибка обработки вебхука: {e}")
        return "ERROR", 500

@app.route("/", methods=['GET'])
def index():
    return "Бот работает!", 200

@app.route("/health", methods=['GET'])
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

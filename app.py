import sys
import os
import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from flask import Flask


from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database.db import Database
from handlers import start, create, list, settings, callback
from keyboards.keyboards import get_reminder_actions_keyboard
from utils.scheduler import setup_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Flask для Render ---
app = Flask(__name__)

@app.route("/")
def index():
    return "Бот работает!", 200

@app.route("/health")
def health():
    return "OK", 200

def run_flask():
    """Запуск Flask в отдельном потоке"""
    app.run(host="0.0.0.0", port=10000)

# --- Telegram бот ---
async def main():
    logger.info("🚀 Запуск бота на Render...")
    
    # Запускаем Flask в фоновом потоке
    thread = threading.Thread(target=run_flask, daemon=True)
    thread.start()
    logger.info("🌐 Flask сервер запущен на порту 10000")
    
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher()
    
    dp.include_router(start.router)
    dp.include_router(create.router)
    dp.include_router(list.router)
    dp.include_router(settings.router)
    dp.include_router(callback.router)
    
    setup_scheduler(bot)
    logger.info("⏰ Планировщик запущен")
    
    logger.info("🔍 Проверка пропущенных напоминаний...")
    db = Database()
    due_reminders = db.get_due_reminders()
    if due_reminders:
        for reminder in due_reminders:
            try:
                await bot.send_message(
                    reminder['user_id'],
                    f"⚠️ **Бот был выключен, прошу прощение за неудобства**\n\n"
                    f"🔔 Напоминание: {reminder['text']}"
                )
                db.disable_reminder(reminder['id'])
            except Exception as e:
                logger.error(f"Ошибка отправки пропущенного напоминания: {e}")
    db.close()
    logger.info("✅ Проверка завершена")
    
    logger.info("🤖 Бот запущен и готов к работе!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("👋 Бот остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

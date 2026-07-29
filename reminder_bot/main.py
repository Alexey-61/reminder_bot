import os
import asyncio
import logging
from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database.db import Database
from handlers import start, create, list, settings, callback
from utils.scheduler import setup_scheduler

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация Flask
app = Flask(__name__)

# Инициализация бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

# Регистрация роутеров
dp.include_router(start.router)
dp.include_router(create.router)
dp.include_router(list.router)
dp.include_router(settings.router)
dp.include_router(callback.router)


@app.before_request
async def startup():
    """Инициализация при старте"""
    logger.info("🚀 Запуск бота...")
    
    # Удаляем старый вебхук
    await bot.delete_webhook()
    
    # Настраиваем планировщик для фоновых задач
    setup_scheduler(bot)
    logger.info("⏰ Планировщик запущен")
    
    logger.info("🤖 Бот готов к работе!")


@app.route("/webhook", methods=['POST'])
async def webhook():
    """Точка входа для вебхуков от Telegram"""
    try:
        data = await request.get_json()
        logger.info(f"📨 Получен вебхук: {data}")
        update = Update.model_validate(data, context={"bot": bot})
        await dp.feed_update(bot, update)
        return "OK", 200
    except Exception as e:
        logger.error(f"❌ Ошибка обработки вебхука: {e}")
        return "ERROR", 500


@app.route("/health", methods=['GET'])
def health():
    """Проверка здоровья сервиса"""
    return "OK", 200


@app.route("/", methods=['GET'])
def root():
    """Корневая страница"""
    return "Бот-напоминалка работает!", 200


# Для локального запуска
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
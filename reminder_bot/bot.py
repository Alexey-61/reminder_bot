import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database.db import Database
from handlers import start, create, list, settings, callback
from utils.scheduler import setup_scheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    """Главная функция запуска бота"""
    logger.info("🚀 Запуск бота на Render...")
    
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(create.router)
    dp.include_router(list.router)
    dp.include_router(settings.router)
    dp.include_router(callback.router)
    
    # Настройка планировщика (напоминания!)
    setup_scheduler(bot)
    logger.info("⏰ Планировщик запущен")
    
    # Проверка пропущенных напоминаний при запуске
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
    
    # Запуск бота (Polling)
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
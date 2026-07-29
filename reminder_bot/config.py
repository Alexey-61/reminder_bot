import os

# Токен из переменных окружения Render
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ Токен не найден! Добавь BOT_TOKEN в Environment Variables на Render.")

# Настройки по умолчанию
DEFAULT_INTERVAL = 5
DEFAULT_MAX_REPEATS = 6
DEFAULT_STOP_WORD = "хватит"
DEFAULT_TIMEZONE = "Europe/Moscow"
DATABASE_PATH = "reminders.db"

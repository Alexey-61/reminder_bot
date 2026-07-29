import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройки по умолчанию
DEFAULT_INTERVAL = 5  # минут
DEFAULT_MAX_REPEATS = 6  # количество повторов
DEFAULT_STOP_WORD = "хватит"
DEFAULT_TIMEZONE = "Europe/Moscow"

# Путь к базе данных
DATABASE_PATH = "reminders.db"

# Проверка токена
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")
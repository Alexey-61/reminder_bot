import requests
from typing import Optional
import pytz
from config import DEFAULT_TIMEZONE


def get_timezone_by_ip(ip: str) -> str:
    """
    Определяет часовой пояс по IP-адресу
    """
    try:
        # Используем бесплатный API для определения времени по IP
        response = requests.get(f"http://ip-api.com/json/{ip}?fields=timezone", timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('timezone') and data['timezone'] in pytz.all_timezones:
                return data['timezone']
    except:
        pass
    return DEFAULT_TIMEZONE


def get_user_timezone(user_id: int, bot) -> str:
    """
    Получает часовой пояс пользователя через Telegram API
    """
    try:
        # Пробуем получить чат, чтобы узнать IP
        # Это не всегда работает, но попробуем
        chat = bot.get_chat(user_id)
        # У Telegram нет прямого метода для получения IP
        # Поэтому используем fallback
        return DEFAULT_TIMEZONE
    except:
        return DEFAULT_TIMEZONE
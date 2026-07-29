import re
from datetime import datetime, timedelta
from dateutil import parser
import pytz
from typing import Optional, Tuple


def parse_reminder_time(text: str, user_timezone: str = "Europe/Moscow") -> Tuple[Optional[datetime], Optional[str], Optional[int]]:
    """
    Парсит текст и возвращает:
    - время (datetime)
    - тип напоминания ('once', 'daily', 'weekly')
    - день недели для weekly (0-6, где 0-понедельник)
    """
    text = text.lower().strip()
    tz = pytz.timezone(user_timezone)
    now = datetime.now(tz)
    
    # Проверка на ежедневное
    if re.search(r'каждый день|ежедневно|каждодневно', text):
        time_match = re.search(r'(\d{1,2})[:.](\d{2})', text)
        if time_match:
            hour, minute = int(time_match.group(1)), int(time_match.group(2))
            remind_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            # Если время уже прошло сегодня, ставим на завтра
            if remind_time <= now:
                remind_time += timedelta(days=1)
            return remind_time, 'daily', None
    
    # Проверка на еженедельное
    weekdays = {
        'понедельник': 0, 'пн': 0,
        'вторник': 1, 'вт': 1,
        'среда': 2, 'ср': 2,
        'четверг': 3, 'чт': 3,
        'пятница': 4, 'пт': 4,
        'суббота': 5, 'сб': 5,
        'воскресенье': 6, 'вс': 6
    }
    
    for day_name, day_num in weekdays.items():
        if day_name in text:
            time_match = re.search(r'(\d{1,2})[:.](\d{2})', text)
            if time_match:
                hour, minute = int(time_match.group(1)), int(time_match.group(2))
                remind_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                # Перемещаем на нужный день недели
                days_ahead = day_num - remind_time.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                remind_time += timedelta(days=days_ahead)
                return remind_time, 'weekly', day_num
    
    # Проверка на "через X минут/часов"
    match = re.search(r'через\s+(\d+)\s*(мин|минут|час|часов)', text)
    if match:
        value = int(match.group(1))
        unit = match.group(2)
        if unit in ['час', 'часов']:
            delta = timedelta(hours=value)
        else:
            delta = timedelta(minutes=value)
        remind_time = now + delta
        return remind_time, 'once', None
    
    # Проверка на "завтра"
    if 'завтра' in text:
        time_match = re.search(r'(\d{1,2})[:.](\d{2})', text)
        if time_match:
            hour, minute = int(time_match.group(1)), int(time_match.group(2))
            remind_time = (now + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
            return remind_time, 'once', None
        else:
            # Завтра в то же время, что и сейчас
            remind_time = now + timedelta(days=1)
            return remind_time, 'once', None
    
    # Проверка на "послезавтра"
    if 'послезавтра' in text:
        time_match = re.search(r'(\d{1,2})[:.](\d{2})', text)
        if time_match:
            hour, minute = int(time_match.group(1)), int(time_match.group(2))
            remind_time = (now + timedelta(days=2)).replace(hour=hour, minute=minute, second=0, microsecond=0)
            return remind_time, 'once', None
    
    # Обычный парсинг даты и времени
    try:
        # Пробуем распарсить как "15:30" или "15.30"
        time_match = re.search(r'(\d{1,2})[:.](\d{2})', text)
        if time_match:
            hour, minute = int(time_match.group(1)), int(time_match.group(2))
            remind_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if remind_time <= now:
                remind_time += timedelta(days=1)
            return remind_time, 'once', None
        
        # Пробуем распарсить через dateutil
        dt = parser.parse(text, tzinfos={'мск': tz})
        if dt.tzinfo is None:
            dt = tz.localize(dt)
        return dt, 'once', None
    except:
        return None, None, None
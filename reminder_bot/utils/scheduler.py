from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import pytz

from database.db import Database
from config import DEFAULT_TIMEZONE

db = Database()
scheduler = AsyncIOScheduler()


def setup_scheduler(bot):
    """Настройка планировщика"""
    # Проверка каждые 30 секунд для большей точности
    scheduler.add_job(
        check_reminders,
        CronTrigger(second="*/30"),
        args=[bot],
        id="check_reminders"
    )
    scheduler.start()


async def check_reminders(bot):
    """Проверка напоминаний"""
    due_reminders = db.get_due_reminders()
    
    for reminder in due_reminders:
        user_id = reminder['user_id']
        reminder_id = reminder['id']
        text = reminder['text']
        reminder_type = reminder['reminder_type']
        remind_time = reminder['remind_time']
        
        # Получаем настройки пользователя
        settings = db.get_user_settings(user_id)
        max_repeats = settings['max_repeats']
        interval = settings['repeat_interval']
        
        try:
            from keyboards.keyboards import get_reminder_actions_keyboard
            
            # Проверяем, не было ли уже отправлено сегодня (для ежедневных)
            if reminder_type == 'daily':
                last_sent = db.cursor.execute(
                    "SELECT last_sent_time FROM reminders WHERE id = ?",
                    (reminder_id,)
                ).fetchone()
                
                if last_sent and last_sent[0]:
                    last_sent_date = datetime.fromisoformat(last_sent[0]).date()
                    today = datetime.now().date()
                    if last_sent_date == today:
                        continue
            
            # Отправляем сообщение
            keyboard = get_reminder_actions_keyboard(reminder_id)
            await bot.send_message(
                user_id,
                f"🔔 **Напоминание!**\n\n{text}",
                reply_markup=keyboard
            )
            
            # Обновляем время последней отправки
            db.cursor.execute(
                "UPDATE reminders SET last_sent_time = ? WHERE id = ?",
                (datetime.now().isoformat(), reminder_id)
            )
            db.conn.commit()
            
            # Обработка повторов
            if reminder['repeat_enabled']:
                count = db.increment_repeat_count(reminder_id)
                
                if count >= max_repeats:
                    db.update_repeat_status(reminder_id, False, 0)
                    await bot.send_message(
                        user_id,
                        f"⏹ Я устал напоминать! Повтор для \"{text}\" отключен. 😴"
                    )
                else:
                    # Следующее напоминание через interval минут от исходного времени
                    next_time = remind_time + timedelta(minutes=interval)
                    db.update_reminder_time(reminder_id, next_time)
            
            else:
                if reminder_type == 'once':
                    db.disable_reminder(reminder_id)
                elif reminder_type in ['daily', 'weekly']:
                    tz = pytz.timezone(settings['timezone'] or DEFAULT_TIMEZONE)
                    now = datetime.now(tz)
                    next_time = remind_time
                    
                    if reminder_type == 'daily':
                        next_time = remind_time + timedelta(days=1)
                    elif reminder_type == 'weekly':
                        next_time = remind_time + timedelta(days=7)
                    
                    db.update_reminder_time(reminder_id, next_time)
                    
        except Exception as e:
            print(f"Ошибка при отправке напоминания {reminder_id}: {e}")
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import os

class Database:
    def __init__(self):
        # База данных в файле рядом с кодом
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'reminders.db')
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Создание таблиц, если их нет"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                stop_word TEXT DEFAULT 'хватит',
                repeat_interval INTEGER DEFAULT 5,
                max_repeats INTEGER DEFAULT 6,
                timezone TEXT DEFAULT 'Europe/Moscow'
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                text TEXT,
                remind_time TEXT,
                reminder_type TEXT,
                week_day INTEGER,
                is_active INTEGER DEFAULT 1,
                repeat_enabled INTEGER DEFAULT 0,
                repeat_count INTEGER DEFAULT 0,
                last_sent_time TEXT,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        self.conn.commit()

    def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """Получить настройки пользователя"""
        self.cursor.execute(
            "SELECT stop_word, repeat_interval, max_repeats, timezone FROM users WHERE user_id = ?",
            (user_id,)
        )
        result = self.cursor.fetchone()
        
        if result:
            return {
                "stop_word": result[0],
                "repeat_interval": result[1],
                "max_repeats": result[2],
                "timezone": result[3]
            }
        else:
            self.cursor.execute(
                "INSERT INTO users (user_id) VALUES (?)",
                (user_id,)
            )
            self.conn.commit()
            return {
                "stop_word": "хватит",
                "repeat_interval": 5,
                "max_repeats": 6,
                "timezone": "Europe/Moscow"
            }

    def update_user_settings(self, user_id: int, **kwargs):
        """Обновить настройки пользователя"""
        for key, value in kwargs.items():
            self.cursor.execute(
                f"UPDATE users SET {key} = ? WHERE user_id = ?",
                (value, user_id)
            )
        self.conn.commit()

    def add_reminder(self, user_id: int, text: str, remind_time: datetime, 
                     reminder_type: str = 'once', week_day: Optional[int] = None) -> int:
        """Добавить новое напоминание"""
        self.cursor.execute("""
            INSERT INTO reminders (
                user_id, text, remind_time, reminder_type, week_day, 
                repeat_enabled, repeat_count, created_at, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            text,
            remind_time.isoformat(),
            reminder_type,
            week_day,
            0,
            0,
            datetime.now().isoformat(),
            1
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_active_reminders(self, user_id: int) -> List[Dict[str, Any]]:
        """Получить все активные напоминания пользователя"""
        self.cursor.execute("""
            SELECT id, text, remind_time, reminder_type, week_day, 
                   repeat_enabled, repeat_count
            FROM reminders
            WHERE user_id = ? AND is_active = 1
            ORDER BY remind_time
        """, (user_id,))
        
        rows = self.cursor.fetchall()
        reminders = []
        for row in rows:
            reminders.append({
                "id": row[0],
                "text": row[1],
                "remind_time": datetime.fromisoformat(row[2]),
                "reminder_type": row[3],
                "week_day": row[4],
                "repeat_enabled": bool(row[5]),
                "repeat_count": row[6]
            })
        return reminders

    def get_reminder(self, reminder_id: int) -> Optional[Dict[str, Any]]:
        """Получить напоминание по ID"""
        self.cursor.execute("""
            SELECT id, user_id, text, remind_time, reminder_type, week_day,
                   is_active, repeat_enabled, repeat_count
            FROM reminders
            WHERE id = ?
        """, (reminder_id,))
        
        row = self.cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "user_id": row[1],
                "text": row[2],
                "remind_time": datetime.fromisoformat(row[3]),
                "reminder_type": row[4],
                "week_day": row[5],
                "is_active": bool(row[6]),
                "repeat_enabled": bool(row[7]),
                "repeat_count": row[8]
            }
        return None

    def delete_reminder(self, reminder_id: int):
        """Удалить напоминание"""
        self.cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        self.conn.commit()

    def disable_reminder(self, reminder_id: int):
        """Отключить напоминание"""
        self.cursor.execute(
            "UPDATE reminders SET is_active = 0 WHERE id = ?",
            (reminder_id,)
        )
        self.conn.commit()

    def update_reminder_time(self, reminder_id: int, new_time: datetime):
        """Обновить время напоминания"""
        self.cursor.execute(
            "UPDATE reminders SET remind_time = ? WHERE id = ?",
            (new_time.isoformat(), reminder_id)
        )
        self.conn.commit()

    def update_repeat_status(self, reminder_id: int, enabled: bool, count: int = 0):
        """Обновить статус повтора"""
        self.cursor.execute(
            "UPDATE reminders SET repeat_enabled = ?, repeat_count = ? WHERE id = ?",
            (1 if enabled else 0, count, reminder_id)
        )
        self.conn.commit()

    def increment_repeat_count(self, reminder_id: int) -> int:
        """Увеличить счетчик повторов"""
        self.cursor.execute(
            "UPDATE reminders SET repeat_count = repeat_count + 1 WHERE id = ?",
            (reminder_id,)
        )
        self.conn.commit()
        self.cursor.execute(
            "SELECT repeat_count FROM reminders WHERE id = ?",
            (reminder_id,)
        )
        return self.cursor.fetchone()[0]

    def get_due_reminders(self) -> List[Dict[str, Any]]:
        """Получить все просроченные активные напоминания"""
        now = datetime.now()
        self.cursor.execute("""
            SELECT id, user_id, text, remind_time, reminder_type, week_day,
                   repeat_enabled, repeat_count
            FROM reminders
            WHERE is_active = 1 AND remind_time <= ?
        """, (now.isoformat(),))
        
        rows = self.cursor.fetchall()
        reminders = []
        for row in rows:
            reminders.append({
                "id": row[0],
                "user_id": row[1],
                "text": row[2],
                "remind_time": datetime.fromisoformat(row[3]),
                "reminder_type": row[4],
                "week_day": row[5],
                "repeat_enabled": bool(row[6]),
                "repeat_count": row[7]
            })
        return reminders

    def close(self):
        """Закрыть соединение с БД"""
        self.conn.close()

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


# ============ REPLY КЛАВИАТУРЫ (внизу экрана) ============

def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="➕ Создать напоминание"),
        KeyboardButton(text="📋 Мои напоминания")
    )
    builder.row(
        KeyboardButton(text="⚙️ Настройки"),
        KeyboardButton(text="❓ Помощь")
    )
    return builder.as_markup(resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отмена")
    return builder.as_markup(resize_keyboard=True)


def get_repeat_choice_keyboard():
    """Клавиатура выбора повтора"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="✅ Да, включить повтор"),
        KeyboardButton(text="❌ Нет, не надо")
    )
    builder.row(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True)


# ============ INLINE КЛАВИАТУРЫ (под сообщениями) ============

def get_reminder_actions_keyboard(reminder_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для управления напоминанием (под сообщением)"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Хватит!",
            callback_data=f"stopit_{reminder_id}"  # 👈 Меняем название
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="❌ Удалить",
            callback_data=f"del_{reminder_id}"  # 👈 Меняем название
        ),
        InlineKeyboardButton(
            text="⏹ Остановить повтор",
            callback_data=f"stoprepeat_{reminder_id}"  # 👈 Меняем название
        )
    )
    return builder.as_markup()


def get_reminder_list_keyboard(reminder_id: int, repeat_enabled: bool) -> InlineKeyboardMarkup:
    """Клавиатура для списка напоминаний"""
    builder = InlineKeyboardBuilder()
    
    if repeat_enabled:
        builder.row(
            InlineKeyboardButton(
                text="⏹ Остановить повтор",
                callback_data=f"stoplist_{reminder_id}"  # 👈 Меняем название
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="❌ Удалить",
            callback_data=f"dellist_{reminder_id}"  # 👈 Меняем название
        )
    )
    return builder.as_markup()


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура настроек"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✏️ Изменить стоп-слово",
            callback_data="settings_stop_word"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⏱ Изменить интервал повтора",
            callback_data="settings_interval"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔢 Изменить количество повторов",
            callback_data="settings_max_repeats"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔙 Назад",
            callback_data="back_to_menu"
        )
    )
    return builder.as_markup()


def get_inline_menu() -> InlineKeyboardMarkup:
    """Инлайн меню в сообщении"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Создать", callback_data="menu_create"),
        InlineKeyboardButton(text="📋 Список", callback_data="menu_list")
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings"),
        InlineKeyboardButton(text="❓ Помощь", callback_data="menu_help")
    )
    return builder.as_markup()
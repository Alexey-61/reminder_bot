from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import Database
from utils.time_parser import parse_reminder_time
from utils.timezone import get_user_timezone
from keyboards.keyboards import get_cancel_keyboard, get_main_menu, get_repeat_choice_keyboard, get_inline_menu

router = Router()
db = Database()


class CreateReminderStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_time = State()
    waiting_for_repeat = State()


@router.message(F.text == "➕ Создать напоминание")
async def start_create_reminder(message: Message, state: FSMContext):
    """Начало создания напоминания"""
    await state.set_state(CreateReminderStates.waiting_for_text)
    await message.answer(
        "📝 Введите текст напоминания:\n\n"
        "Например: `Позвонить маме` или `Купить хлеб`",
        reply_markup=get_cancel_keyboard()
    )


@router.message(CreateReminderStates.waiting_for_text, F.text != "❌ Отмена")
async def process_reminder_text(message: Message, state: FSMContext):
    """Получение текста напоминания"""
    await state.update_data(text=message.text)
    await state.set_state(CreateReminderStates.waiting_for_time)
    
    await message.answer(
        "⏰ Введите время напоминания:\n\n"
        "**Примеры:**\n"
        "• `15:30` - сегодня в 15:30\n"
        "• `завтра 10:00` - завтра в 10:00\n"
        "• `каждый день 09:00` - ежедневно\n"
        "• `каждый понедельник 18:30` - еженедельно\n"
        "• `через 30 минут` - через 30 минут",
        reply_markup=get_cancel_keyboard()
    )


@router.message(CreateReminderStates.waiting_for_time, F.text != "❌ Отмена")
async def process_reminder_time(message: Message, state: FSMContext):
    """Получение времени напоминания"""
    user_id = message.from_user.id
    settings = db.get_user_settings(user_id)
    timezone = settings['timezone']
    
    remind_time, reminder_type, week_day = parse_reminder_time(message.text, timezone)
    
    if remind_time is None:
        await message.answer(
            "❌ Не удалось распознать время. Попробуйте еще раз:\n\n"
            "Примеры: `15:30`, `завтра 10:00`, `каждый день 09:00`",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Сохраняем данные
    await state.update_data(
        remind_time=remind_time,
        reminder_type=reminder_type,
        week_day=week_day
    )
    
    # Спрашиваем про повтор
    await state.set_state(CreateReminderStates.waiting_for_repeat)
    
    # Получаем настройки пользователя, чтобы узнать интервал
    interval = settings['repeat_interval']
    
    repeat_text = (
        "🔄 Включить повторение?\n\n"
        f"Бот будет отправлять это напоминание **каждые {interval} минут**, "
        "пока вы не скажете 'Хватит' или не нажмете кнопку."
    )
    
    keyboard = get_repeat_choice_keyboard()
    await message.answer(repeat_text, reply_markup=keyboard)


@router.message(CreateReminderStates.waiting_for_repeat)
async def process_repeat_choice(message: Message, state: FSMContext):
    """Обработка выбора повтора"""
    user_id = message.from_user.id
    
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "❌ Создание отменено",
            reply_markup=get_main_menu()
        )
        return
    
    if message.text not in ["✅ Да, включить повтор", "❌ Нет, не надо"]:
        await message.answer("Пожалуйста, выберите один из вариантов:")
        return
    
    repeat_enabled = message.text == "✅ Да, включить повтор"
    
    # Получаем данные из состояния
    data = await state.get_data()
    text = data['text']
    remind_time = data['remind_time']
    reminder_type = data['reminder_type']
    week_day = data.get('week_day')
    
    # Сохраняем в БД
    reminder_id = db.add_reminder(
        user_id=user_id,
        text=text,
        remind_time=remind_time,
        reminder_type=reminder_type,
        week_day=week_day
    )
    
    if repeat_enabled:
        db.update_repeat_status(reminder_id, True, 0)
    
    # Формируем ответ
    time_str = remind_time.strftime("%d.%m.%Y в %H:%M")
    type_names = {
        'once': 'Одноразовое',
        'daily': 'Ежедневное',
        'weekly': 'Еженедельное'
    }
    
    response = (
        f"✅ Напоминание создано!\n\n"
        f"📝 Текст: {text}\n"
        f"⏰ Время: {time_str}\n"
        f"📌 Тип: {type_names.get(reminder_type, 'Одноразовое')}\n"
        f"🔄 Повтор: {'Включен' if repeat_enabled else 'Выключен'}"
    )
    
    await state.clear()
    await message.answer(response, reply_markup=get_main_menu())


@router.message(F.text == "❌ Отмена")
async def cancel_creation(message: Message, state: FSMContext):
    """Отмена создания напоминания"""
    await state.clear()
    await message.answer(
        "❌ Создание отменено",
        reply_markup=get_main_menu()
    )


@router.callback_query(F.data == "cancel_creation")
async def cancel_creation_inline(callback: CallbackQuery, state: FSMContext):
    """Отмена создания через инлайн-кнопку"""
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "❌ Создание отменено",
        reply_markup=get_inline_menu()
    )
    await callback.answer()
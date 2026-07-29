from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command

from database.db import Database
from keyboards.keyboards import get_reminder_list_keyboard, get_main_menu

router = Router()
db = Database()


@router.message(F.text == "📋 Мои напоминания")
@router.message(Command("list"))
async def show_reminders(message: Message):
    """Показать список напоминаний с картинкой"""
    user_id = message.from_user.id
    reminders = db.get_active_reminders(user_id)
    
    photo = FSInputFile("images/list.jpg")
    
    if not reminders:
        text = "📭 У вас нет активных напоминаний.\n\nСоздайте новое через кнопку ➕ Создать напоминание"
        try:
            await message.answer_photo(
                photo=photo,
                caption=text,
                reply_markup=get_main_menu()
            )
        except:
            await message.answer(text, reply_markup=get_main_menu())
        return
    
    text = "📋 **Ваши напоминания:**\n\n"
    for i, rem in enumerate(reminders, 1):
        time_str = rem['remind_time'].strftime("%d.%m.%Y %H:%M")
        type_names = {
            'once': '🔹 Одноразовое',
            'daily': '🔸 Ежедневное',
            'weekly': '🔹 Еженедельное'
        }
        repeat_status = "🔄 Повтор включен" if rem['repeat_enabled'] else "⏸ Повтор выключен"
        
        text += (
            f"**{i}. ID: `{rem['id']}`**\n"
            f"📝 {rem['text']}\n"
            f"⏰ {time_str}\n"
            f"{type_names.get(rem['reminder_type'], 'Одноразовое')}\n"
            f"{repeat_status}\n\n"
        )
    
    try:
        await message.answer_photo(
            photo=photo,
            caption=text,
            reply_markup=get_main_menu()
        )
    except:
        await message.answer(text, reply_markup=get_main_menu())
    
    # Отправляем каждое напоминание с кнопками
    for rem in reminders:
        keyboard = get_reminder_list_keyboard(rem['id'], rem['repeat_enabled'])
        time_str = rem['remind_time'].strftime("%d.%m.%Y %H:%M")
        await message.answer(
            f"🔔 **{rem['text']}**\n⏰ {time_str}\nID: `{rem['id']}`",
            reply_markup=keyboard
        )


@router.callback_query(F.data.startswith("delete_"))
async def delete_reminder(callback: CallbackQuery):
    """Удалить напоминание"""
    try:
        reminder_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("❌ Неверный формат кнопки", show_alert=True)
        return
    
    reminder = db.get_reminder(reminder_id)
    
    if not reminder or reminder['user_id'] != callback.from_user.id:
        await callback.answer("❌ Напоминание не найдено", show_alert=True)
        return
    
    db.delete_reminder(reminder_id)
    await callback.message.delete()
    await callback.answer("✅ Напоминание удалено", show_alert=True)


@router.callback_query(F.data.startswith("stop_"))
async def stop_repeat_from_list(callback: CallbackQuery):
    """Остановить повтор из списка"""
    try:
        reminder_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("❌ Неверный формат кнопки", show_alert=True)
        return
    
    reminder = db.get_reminder(reminder_id)
    
    if not reminder or reminder['user_id'] != callback.from_user.id:
        await callback.answer("❌ Напоминание не найдено", show_alert=True)
        return
    
    db.update_repeat_status(reminder_id, False, 0)
    await callback.message.edit_reply_markup(
        reply_markup=get_reminder_list_keyboard(reminder_id, False)
    )
    await callback.answer("⏹ Повтор остановлен", show_alert=True)
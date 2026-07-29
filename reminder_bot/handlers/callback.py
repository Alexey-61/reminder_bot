from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from database.db import Database
from keyboards.keyboards import get_reminder_actions_keyboard, get_reminder_list_keyboard, get_inline_menu

router = Router()
db = Database()


# ===== КНОПКА "ХВАТИТ!" В СООБЩЕНИИ =====
@router.callback_query(F.data.startswith("stopit_"))
async def stop_repeat_from_message(callback: CallbackQuery):
    """Хватит! - удаляем напоминание"""
    try:
        reminder_id = int(callback.data.split("_")[1])
    except:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    reminder = db.get_reminder(reminder_id)
    if not reminder or reminder['user_id'] != callback.from_user.id:
        await callback.answer("❌ Не найдено", show_alert=True)
        return
    
    # Удаляем из БД
    db.delete_reminder(reminder_id)
    
    # Удаляем сообщение
    try:
        await callback.message.delete()
    except:
        pass
    
    # Отправляем меню
    await callback.message.answer(
        "✅ Напоминание выполнено!",
        reply_markup=get_inline_menu()
    )
    await callback.answer("✅ Готово!")


# ===== КНОПКА "УДАЛИТЬ" В СООБЩЕНИИ =====
@router.callback_query(F.data.startswith("del_"))
async def delete_reminder_from_message(callback: CallbackQuery):
    """Удалить напоминание"""
    try:
        reminder_id = int(callback.data.split("_")[1])
    except:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    reminder = db.get_reminder(reminder_id)
    if not reminder or reminder['user_id'] != callback.from_user.id:
        await callback.answer("❌ Не найдено", show_alert=True)
        return
    
    db.delete_reminder(reminder_id)
    
    try:
        await callback.message.delete()
    except:
        pass
    
    await callback.message.answer(
        "✅ Напоминание удалено!",
        reply_markup=get_inline_menu()
    )
    await callback.answer("✅ Удалено!")


# ===== КНОПКА "ОСТАНОВИТЬ ПОВТОР" В СООБЩЕНИИ =====
@router.callback_query(F.data.startswith("stoprepeat_"))
async def stop_repeat_in_message(callback: CallbackQuery):
    """Остановить повтор (но не удалять)"""
    try:
        reminder_id = int(callback.data.split("_")[1])
    except:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    reminder = db.get_reminder(reminder_id)
    if not reminder or reminder['user_id'] != callback.from_user.id:
        await callback.answer("❌ Не найдено", show_alert=True)
        return
    
    # Просто останавливаем повтор
    db.update_repeat_status(reminder_id, False, 0)
    
    # Обновляем кнопки
    await callback.message.edit_reply_markup(
        reply_markup=get_reminder_actions_keyboard(reminder_id)
    )
    await callback.answer("⏹ Повтор остановлен!")


# ===== КНОПКА "ОСТАНОВИТЬ ПОВТОР" В СПИСКЕ =====
@router.callback_query(F.data.startswith("stoplist_"))
async def stop_repeat_in_list(callback: CallbackQuery):
    """Остановить повтор из списка"""
    try:
        reminder_id = int(callback.data.split("_")[1])
    except:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    reminder = db.get_reminder(reminder_id)
    if not reminder or reminder['user_id'] != callback.from_user.id:
        await callback.answer("❌ Не найдено", show_alert=True)
        return
    
    db.update_repeat_status(reminder_id, False, 0)
    
    await callback.message.edit_reply_markup(
        reply_markup=get_reminder_list_keyboard(reminder_id, False)
    )
    await callback.answer("⏹ Повтор остановлен!")


# ===== КНОПКА "УДАЛИТЬ" В СПИСКЕ =====
@router.callback_query(F.data.startswith("dellist_"))
async def delete_from_list(callback: CallbackQuery):
    """Удалить из списка"""
    try:
        reminder_id = int(callback.data.split("_")[1])
    except:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    reminder = db.get_reminder(reminder_id)
    if not reminder or reminder['user_id'] != callback.from_user.id:
        await callback.answer("❌ Не найдено", show_alert=True)
        return
    
    db.delete_reminder(reminder_id)
    await callback.message.delete()
    await callback.answer("✅ Удалено!")


# ===== СТОП-СЛОВО =====
@router.message(F.text)
async def check_stop_word(message: Message):
    """Проверка стоп-слова - УДАЛЯЕТ напоминание"""
    user_id = message.from_user.id
    settings = db.get_user_settings(user_id)
    stop_word = settings['stop_word'].lower()
    
    if stop_word in message.text.lower():
        reminders = db.get_active_reminders(user_id)
        deleted = False
        
        for rem in reminders:
            if rem['repeat_enabled']:
                # 👇 УДАЛЯЕМ напоминание, а не просто останавливаем повтор
                db.delete_reminder(rem['id'])
                deleted = True
                await message.answer(f"✅ Напоминание \"{rem['text']}\" выполнено и удалено!")
        
        if not deleted:
            await message.answer("✅ Нет активных напоминаний с повтором.")


# ===== МЕНЮ =====
@router.callback_query(F.data == "menu_create")
async def menu_create(callback: CallbackQuery):
    """Создать"""
    await callback.answer()
    from handlers.create import start_create_reminder
    
    class FakeMessage:
        def __init__(self, cb):
            self.from_user = cb.from_user
            self.chat = cb.message.chat
            self.text = "➕ Создать напоминание"
            self.answer = cb.message.answer
            self.reply_markup = None
    
    await start_create_reminder(FakeMessage(callback), None)


@router.callback_query(F.data == "menu_list")
async def menu_list(callback: CallbackQuery):
    """Список"""
    await callback.answer()
    from handlers.list import show_reminders
    await show_reminders(callback.message)


@router.callback_query(F.data == "menu_settings")
async def menu_settings(callback: CallbackQuery):
    """Настройки"""
    await callback.answer()
    from handlers.settings import show_settings
    await show_settings(callback.message)


@router.callback_query(F.data == "menu_help")
async def menu_help(callback: CallbackQuery):
    """Помощь"""
    await callback.answer()
    from handlers.start import cmd_help
    await cmd_help(callback.message)
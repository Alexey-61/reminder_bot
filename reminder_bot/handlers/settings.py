from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import Database
from keyboards.keyboards import get_settings_keyboard, get_main_menu, get_inline_menu

router = Router()
db = Database()


class SettingsStates(StatesGroup):
    waiting_for_stop_word = State()
    waiting_for_interval = State()
    waiting_for_max_repeats = State()


@router.message(F.text == "⚙️ Настройки")
async def show_settings(message: Message):
    """Показать настройки с картинкой"""
    user_id = message.from_user.id
    settings = db.get_user_settings(user_id)
    
    photo = FSInputFile("images/settings.jpg")
    
    text = (
        "⚙️ **Ваши настройки:**\n\n"
        f"📝 Стоп-слово: `{settings['stop_word']}`\n"
        f"⏱ Интервал повтора: {settings['repeat_interval']} минут\n"
        f"🔢 Количество повторов: {settings['max_repeats']}\n\n"
        "Выберите, что хотите изменить:"
    )
    
    try:
        await message.answer_photo(
            photo=photo,
            caption=text,
            reply_markup=get_settings_keyboard()
        )
    except:
        await message.answer(text, reply_markup=get_settings_keyboard())


@router.callback_query(F.data == "settings_stop_word")
async def change_stop_word(callback: CallbackQuery, state: FSMContext):
    """Изменить стоп-слово"""
    await state.set_state(SettingsStates.waiting_for_stop_word)
    await callback.message.edit_text(
        "✏️ Введите новое стоп-слово:\n\n"
        "Это слово будет останавливать повтор напоминаний.\n"
        "По умолчанию: хватит"
    )
    await callback.answer()


@router.message(SettingsStates.waiting_for_stop_word)
async def process_stop_word(message: Message, state: FSMContext):
    """Обработка нового стоп-слова"""
    user_id = message.from_user.id
    word = message.text.strip().lower()
    
    if len(word) < 1:
        await message.answer("❌ Слово не может быть пустым.")
        return
    
    db.update_user_settings(user_id, stop_word=word)
    await state.clear()
    
    settings = db.get_user_settings(user_id)
    text = (
        "⚙️ **Ваши настройки:**\n\n"
        f"📝 Стоп-слово: `{settings['stop_word']}`\n"
        f"⏱ Интервал повтора: {settings['repeat_interval']} минут\n"
        f"🔢 Количество повторов: {settings['max_repeats']}\n\n"
        "Выберите, что хотите изменить:"
    )
    
    await message.answer(
        f"✅ Стоп-слово изменено на: `{word}`\n\n{text}",
        reply_markup=get_settings_keyboard()
    )


@router.callback_query(F.data == "settings_interval")
async def change_interval(callback: CallbackQuery, state: FSMContext):
    """Изменить интервал повтора"""
    await state.set_state(SettingsStates.waiting_for_interval)
    await callback.message.edit_text(
        "⏱ Введите интервал повтора в минутах:\n\n"
        "Например: 5 (каждые 5 минут)\n"
        "По умолчанию: 5 минут"
    )
    await callback.answer()


@router.message(SettingsStates.waiting_for_interval)
async def process_interval(message: Message, state: FSMContext):
    """Обработка нового интервала"""
    user_id = message.from_user.id
    
    try:
        interval = int(message.text.strip())
        if interval < 1 or interval > 60:
            await message.answer("❌ Введите число от 1 до 60.")
            return
    except:
        await message.answer("❌ Введите целое число (от 1 до 60).")
        return
    
    db.update_user_settings(user_id, repeat_interval=interval)
    await state.clear()
    
    settings = db.get_user_settings(user_id)
    text = (
        "⚙️ **Ваши настройки:**\n\n"
        f"📝 Стоп-слово: `{settings['stop_word']}`\n"
        f"⏱ Интервал повтора: {settings['repeat_interval']} минут\n"
        f"🔢 Количество повторов: {settings['max_repeats']}\n\n"
        "Выберите, что хотите изменить:"
    )
    
    await message.answer(
        f"✅ Интервал изменен на: {interval} минут\n\n{text}",
        reply_markup=get_settings_keyboard()
    )


@router.callback_query(F.data == "settings_max_repeats")
async def change_max_repeats(callback: CallbackQuery, state: FSMContext):
    """Изменить количество повторов"""
    await state.set_state(SettingsStates.waiting_for_max_repeats)
    await callback.message.edit_text(
        "🔢 Введите количество повторов:\n\n"
        "Сколько раз бот будет повторять напоминание.\n"
        "По умолчанию: 6 (30 минут)"
    )
    await callback.answer()


@router.message(SettingsStates.waiting_for_max_repeats)
async def process_max_repeats(message: Message, state: FSMContext):
    """Обработка нового количества повторов"""
    user_id = message.from_user.id
    
    try:
        max_repeats = int(message.text.strip())
        if max_repeats < 1 or max_repeats > 20:
            await message.answer("❌ Введите число от 1 до 20.")
            return
    except:
        await message.answer("❌ Введите целое число (от 1 до 20).")
        return
    
    db.update_user_settings(user_id, max_repeats=max_repeats)
    await state.clear()
    
    settings = db.get_user_settings(user_id)
    text = (
        "⚙️ **Ваши настройки:**\n\n"
        f"📝 Стоп-слово: `{settings['stop_word']}`\n"
        f"⏱ Интервал повтора: {settings['repeat_interval']} минут\n"
        f"🔢 Количество повторов: {settings['max_repeats']}\n\n"
        "Выберите, что хотите изменить:"
    )
    
    await message.answer(
        f"✅ Количество повторов изменено на: {max_repeats}\n\n{text}",
        reply_markup=get_settings_keyboard()
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_settings(callback: CallbackQuery, state: FSMContext):
    """Вернуться в меню из настроек"""
    await state.clear()
    
    try:
        await callback.message.edit_text(
            "📋 **Меню:**\n\nВыберите действие:",
            reply_markup=get_inline_menu()
        )
    except:
        await callback.message.delete()
        await callback.message.answer(
            "📋 **Меню:**\n\nВыберите действие:",
            reply_markup=get_inline_menu()
        )
    
    await callback.answer()
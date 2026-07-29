from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.keyboards import get_main_menu, get_inline_menu
from database.db import Database

router = Router()
db = Database()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    db.get_user_settings(user_id)
    
    welcome_text = (
        "👋 Привет! Я бот-напоминалка.\n\n"
        "Я помогу тебе ничего не забыть!\n\n"
        "📌 **Что я умею:**\n"
        "• Создавать одноразовые напоминания\n"
        "• Ежедневные и еженедельные напоминания\n"
        "• Повторять напоминания каждые 5 минут\n"
        "• Останавливать повтор по слову \"хватит\"\n\n"
        "Используй кнопки ниже, чтобы начать! 🚀"
    )
    
    await message.answer(welcome_text)
    await message.answer(
        "📋 **Меню:**\n\nВыберите действие:",
        reply_markup=get_inline_menu()
    )


@router.message(F.text == "📋 Меню")
async def show_menu(message: Message):
    """Показать меню по команде"""
    await message.answer(
        "📋 **Меню:**\n\nВыберите действие:",
        reply_markup=get_inline_menu()
    )


@router.callback_query(F.data == "menu_create")
async def menu_create(callback: CallbackQuery, state: FSMContext):
    """Кнопка 'Создать' в меню"""
    await callback.answer()
    from handlers.create import start_create_reminder
    
    class FakeMessage:
        def __init__(self, cb):
            self.from_user = cb.from_user
            self.chat = cb.message.chat
            self.text = "➕ Создать напоминание"
            self.answer = cb.message.answer
            self.reply_markup = None
    
    fake_msg = FakeMessage(callback)
    await start_create_reminder(fake_msg, state)


@router.callback_query(F.data == "menu_list")
async def menu_list(callback: CallbackQuery):
    """Кнопка 'Список' в меню"""
    await callback.answer()
    from handlers.list import show_reminders
    await show_reminders(callback.message)


@router.callback_query(F.data == "menu_settings")
async def menu_settings(callback: CallbackQuery):
    """Кнопка 'Настройки' в меню"""
    await callback.answer()
    from handlers.settings import show_settings
    await show_settings(callback.message)


@router.callback_query(F.data == "menu_help")
async def menu_help(callback: CallbackQuery):
    """Кнопка 'Помощь' в меню"""
    await callback.answer()
    await cmd_help(callback.message)


@router.message(F.text == "❓ Помощь")
@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help и кнопки Помощь"""
    help_text = (
        "❓ **Как пользоваться ботом:**\n\n"
        "**➕ Создать напоминание**\n"
        "Бот попросит ввести текст, затем время.\n\n"
        "**Форматы времени:**\n"
        "• `15:30` - сегодня в 15:30\n"
        "• `завтра 10:00` - завтра в 10:00\n"
        "• `каждый день 09:00` - ежедневно\n"
        "• `каждый понедельник 18:30` - еженедельно\n"
        "• `через 30 минут` - через 30 минут\n\n"
        "**📋 Мои напоминания**\n"
        "Показывает все активные напоминания.\n\n"
        "**⚙️ Настройки**\n"
        "• Стоп-слово (по умолчанию: `хватит`)\n"
        "• Интервал повтора (по умолчанию: 5 мин)\n"
        "• Количество повторов (по умолчанию: 6)\n\n"
        "**Команды:**\n"
        "/start - Главное меню\n"
        "/list - Список напоминаний\n"
        "/help - Помощь"
    )
    await message.answer(help_text, reply_markup=get_main_menu())
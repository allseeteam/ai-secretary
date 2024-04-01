import logging

from telegram import Update
from telegram.ext import ContextTypes

from database import add_user_to_db
from inline_keyboard_markups import create_main_menu_markup


async def handle_start(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id: int = update.effective_chat.id
    username: str = update.effective_user.username

    add_user_to_db(chat_id, username)
    logging.info(f"User {username} started the bot")

    await context.bot.send_message(
        chat_id=chat_id,
        text="Привет! "
             "Я - ваш ИИ-секретарь, готовый помочь в организации вашего рабочего дня. "
             "Хотите сделать свои записи встреч более удобными и продуктивными? "
             "Добро пожаловать!",
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text="Что сегодня на повестке? "
             "Добавить новую запись или задать вопросы по уже сохраненным?",
        reply_markup=create_main_menu_markup()
    )

from database import add_user_to_db
from markups import create_main_menu_markup
from telegram import Update
from telegram.ext import ContextTypes


async def handle_start(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id: int = update.effective_chat.id
    username: str = update.effective_user.username

    add_user_to_db(chat_id, username)

    await context.bot.send_message(
        chat_id=chat_id,
        text="Привет! Я — ваш AI-секретарь. Чем могу помочь?",
        reply_markup=create_main_menu_markup()
    )

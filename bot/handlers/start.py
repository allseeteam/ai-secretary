from telegram import Update
from telegram.ext import ContextTypes
from database import add_user_to_db


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    username = update.effective_user.username
    add_user_to_db(chat_id, username)
    await context.bot.send_message(chat_id=chat_id, text="Привет! Теперь вы в базе данных.")

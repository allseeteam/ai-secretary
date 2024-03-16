from database import add_user_to_db
from markups import get_main_menu_markup
from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    username = update.effective_user.username
    add_user_to_db(chat_id, username)
    reply_markup = get_main_menu_markup()
    await context.bot.send_message(chat_id=chat_id, text="Привет! Чем могу помочь?", reply_markup=reply_markup)

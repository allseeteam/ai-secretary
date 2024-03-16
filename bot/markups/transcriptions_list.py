from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, CallbackQuery
from telegram.ext import CallbackQueryHandler, ConversationHandler, ContextTypes
from typing import List
from database import get_user_transcriptions


def create_transcriptions_list_markup(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> InlineKeyboardMarkup:
    query: CallbackQuery = update.callback_query
    chat_id: int = query.message.chat_id

    transcriptions: List[tuple] = get_user_transcriptions(chat_id)

    keyboard = [
        [InlineKeyboardButton(transcription[0], callback_data=f"transcription_menu:{transcription[0]}")]
        for transcription in transcriptions
    ]
    keyboard.append([InlineKeyboardButton("Вернуться в главное меню", callback_data="main_menu")])

    return InlineKeyboardMarkup(keyboard)

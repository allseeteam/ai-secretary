from typing import List

from database import get_user_transcriptions_with_given_status
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, CallbackQuery
from telegram.ext import ContextTypes


def create_done_transcriptions_menu_markup(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> InlineKeyboardMarkup:
    query: CallbackQuery = update.callback_query
    chat_id: int = query.message.chat_id

    done_transcriptions: List[tuple] = get_user_transcriptions_with_given_status(chat_id, "Transcribed")

    keyboard = [
        [InlineKeyboardButton(transcription[0], callback_data=f"change_menu_transcription:{transcription[0]}")]
        for transcription in done_transcriptions
    ]
    keyboard.append([InlineKeyboardButton("« Вернуться в главное меню", callback_data="change_menu_main")])

    return InlineKeyboardMarkup(keyboard)

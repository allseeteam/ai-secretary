from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, CallbackQuery
from telegram.ext import CallbackQueryHandler, ConversationHandler, ContextTypes
from typing import List
from database import get_user_transcriptions


def create_transcription_menu_markup(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> InlineKeyboardMarkup:
    callback_query: CallbackQuery = update.callback_query
    transcription_id: str = callback_query.data.split("_")[1]

    keyboard = [
        [InlineKeyboardButton("Проверить статус", callback_data=f"check_transcription_status:{transcription_id}")],
        [InlineKeyboardButton("Получить транскрипцию", callback_data=f"get_transcription_text:{transcription_id}")],
        [InlineKeyboardButton("Вернуться к списку транскрипции", callback_data="show_transcriptions")],
        [InlineKeyboardButton("Вернуться в главное меню", callback_data="main_menu")]]

    return InlineKeyboardMarkup(keyboard)

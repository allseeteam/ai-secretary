from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    CallbackQuery
)
from telegram.ext import ContextTypes


def create_transcription_menu_markup(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> InlineKeyboardMarkup:
    callback_query: CallbackQuery = update.callback_query
    transcription_id: str = callback_query.data.split(":")[-1]

    keyboard = [
        [InlineKeyboardButton("📜 Текст", callback_data=f"change_menu_transcription_text:{transcription_id}")],
        [InlineKeyboardButton("💬 Обсудить", callback_data=f"discuss_transcription:{transcription_id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="change_menu_done_transcriptions")],
        [InlineKeyboardButton("🏠 В меню", callback_data="change_menu_main")]
    ]

    return InlineKeyboardMarkup(keyboard)


def create_transcription_menu_markup_without_callback(transcription_id: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📜 Текст", callback_data=f"change_menu_transcription_text:{transcription_id}")],
        [InlineKeyboardButton("💬 Обсудить", callback_data=f"discuss_transcription:{transcription_id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="change_menu_done_transcriptions")],
        [InlineKeyboardButton("🏠 В меню", callback_data="change_menu_main")]
    ]

    return InlineKeyboardMarkup(keyboard)

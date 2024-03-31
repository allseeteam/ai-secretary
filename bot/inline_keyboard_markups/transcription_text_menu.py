from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    CallbackQuery
)
from telegram.ext import ContextTypes


def create_transcription_text_menu_markup(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> InlineKeyboardMarkup:
    callback_query: CallbackQuery = update.callback_query
    transcription_id: str = callback_query.data.split(":")[-1]

    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data=f"change_menu_transcription:{transcription_id}")],
        [InlineKeyboardButton("💾 К записям", callback_data="change_menu_done_transcriptions")],
        [InlineKeyboardButton("🏠 В меню", callback_data="change_menu_main")]]

    return InlineKeyboardMarkup(keyboard)

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


def create_main_menu_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📂 Сохранённые", callback_data='change_menu_done_transcriptions')],
        [InlineKeyboardButton("➕ Добавить", callback_data='add_new_transcription')]
    ]

    return InlineKeyboardMarkup(keyboard)

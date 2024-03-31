from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


def create_cancel_adding_new_transcription_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Отмена", callback_data='cancel_adding_new_transcription')]
    ]

    return InlineKeyboardMarkup(keyboard)

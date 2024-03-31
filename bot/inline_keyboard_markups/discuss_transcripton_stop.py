from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


def create_stop_transcription_discussion_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Закончить обсуждение", callback_data='stop_transcription_discussion')]
    ]

    return InlineKeyboardMarkup(keyboard)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def create_main_menu_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Мои транскрипции", callback_data='my_transcriptions')],
        [InlineKeyboardButton("Добавить транскрипцию", callback_data='add_transcription')]
    ]

    return InlineKeyboardMarkup(keyboard)

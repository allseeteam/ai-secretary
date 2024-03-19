from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def create_main_menu_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("Завершенные транскрипции️", callback_data='change_menu_done_transcriptions')],
        [InlineKeyboardButton("Добавить транскрипцию", callback_data='scenario_add_transcription_start')]
    ]

    return InlineKeyboardMarkup(keyboard)

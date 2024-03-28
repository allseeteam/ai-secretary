from telegram import ReplyKeyboardMarkup


def create_cancel_adding_new_transcription_markup() -> ReplyKeyboardMarkup:
    keyboard = [['Отмена']]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

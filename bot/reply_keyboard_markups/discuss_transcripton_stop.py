from telegram import ReplyKeyboardMarkup


def create_stop_transcription_discussion_markup() -> ReplyKeyboardMarkup:
    keyboard = [['Закончить обсуждение']]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

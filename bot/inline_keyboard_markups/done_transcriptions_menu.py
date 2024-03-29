from typing import (
    List,
    Dict,
    Any
)

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    CallbackQuery
)
from telegram.ext import ContextTypes

from database import get_all_user_transcriptions_with_given_status


# noinspection PyUnusedLocal
def create_done_transcriptions_menu_markup(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> InlineKeyboardMarkup:
    query: CallbackQuery = update.callback_query
    # noinspection PyUnresolvedReferences
    chat_id: int = query.message.chat_id

    done_transcriptions: List[Dict[str, Any]] = []
    for transcripton_status in [
        "Transcribed",
        "Transcribed and notified",
        "Transcribed and failed to notify"
    ]:
        done_transcriptions += get_all_user_transcriptions_with_given_status(
            chat_id,
            transcripton_status,
            ["id", "title"]
        )

    keyboard = [
        [InlineKeyboardButton(transcription['title'], callback_data=f"change_menu_transcription:{transcription['id']}")]
        for transcription in done_transcriptions
    ]
    keyboard.append([InlineKeyboardButton("« Вернуться в главное меню", callback_data="change_menu_main")])

    return InlineKeyboardMarkup(keyboard)

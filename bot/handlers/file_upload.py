from typing import Coroutine

from database import add_transcription_to_db
from markups import create_main_menu_markup
from telegram import Update
from telegram.ext import ContextTypes


async def handle_new_transcription_audio(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    audio_file_id: str = update.message.audio.file_id
    chat_id: int = update.effective_chat.id
    transcription_title: str = context.user_data.get('new_transcription_title', 'Без названия')

    audio_file: Coroutine = await context.bot.get_file(audio_file_id)
    audio_file_path: str = audio_file.file_path

    add_transcription_to_db(
        chat_id,
        transcription_title,
        audio_file_path,
        "Awaiting upload to transcription API"
    )

    await update.message.reply_text(
        text=f"Ваша транскрипция '{transcription_title}' добавлена в очередь обработки. Чем я могу ещё помочь?",
        reply_markup=create_main_menu_markup()
    )

    context.user_data['awaiting_new_transcription_audio'] = False
    context.user_data.pop('new_transcription_title', None)


async def handle_audio(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    if context.user_data.get('awaiting_new_transcription_audio'):
        await handle_new_transcription_audio(update, context)

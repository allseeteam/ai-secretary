import asyncio
from typing import Coroutine

from database import add_transcription_to_db, add_transcription_text_to_db, update_transcription_status
from telegram import Update
from telegram.ext import ContextTypes


async def handle_audio(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    if context.user_data.get('awaiting_transcription_audio'):
        audio_file_id: str = update.message.audio.file_id
        chat_id: int = update.effective_chat.id
        transcription_title: str = context.user_data.get('transcription_title', 'Без названия')

        audio_file: Coroutine = await context.bot.get_file(audio_file_id)
        audio_file_path: str = audio_file.file_path

        add_transcription_to_db(
            chat_id,
            transcription_title,
            audio_file_path,
            "Awaiting upload to transcription API"
        )
        await update.message.reply_text(
            f"Транскрипция '{transcription_title}' добавлена, aудиофайл находится в обработке."
        )

        context.user_data['awaiting_audio'] = False
        context.user_data.pop('transcription_title', None)

    else:
        await update.message.reply_text(
            "Для добавления новой транскрипции выберите соответствующий пункт в меню."
        )

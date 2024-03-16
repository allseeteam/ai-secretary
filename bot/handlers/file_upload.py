from telegram import Update
from telegram.ext import ContextTypes
from database import add_transcription_to_db, add_transcription_result, update_transcription_status
import asyncio


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_audio'):
        audio_file_id = update.message.audio.file_id
        chat_id = update.effective_chat.id
        title = context.user_data.get('transcription_title', 'Без названия')
        file = await context.bot.get_file(audio_file_id)
        file_path = file.file_path
        transcription_id = add_transcription_to_db(chat_id, title, file_path, "в обработке")
        await update.message.reply_text(f"Транскрипция '{title}' добавлена, файл находится в обработке.")
        await asyncio.sleep(5)
        add_transcription_result(transcription_id, "Это тестовый результат транскрипции.")
        update_transcription_status(transcription_id, "обработано")
        await update.message.reply_text("Обработка завершена!")
        context.user_data['awaiting_audio'] = False
        context.user_data.pop('transcription_title', None)
    else:
        await update.message.reply_text("Для добавления транскрипции выберите соответствующий пункт в меню.")

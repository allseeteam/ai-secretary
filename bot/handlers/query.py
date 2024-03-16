from telegram import Update
from telegram.ext import ContextTypes


async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'my_transcriptions':
        await query.edit_message_text(text="Список ваших транскрипций: ...")
    elif query.data == 'add_transcription':
        await query.edit_message_text(text="Функция добавления транскрипции: ...")

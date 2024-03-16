from telegram import Update
from telegram.ext import ContextTypes


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(context.user_data.get('adding_transcription'))
    if context.user_data.get('adding_transcription'):
        context.user_data['transcription_title'] = update.message.text
        context.user_data['awaiting_audio'] = True
        context.user_data['adding_transcription'] = False
        await update.message.reply_text("Теперь отправьте аудиозапись.")

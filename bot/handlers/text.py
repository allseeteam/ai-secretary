from telegram import Update
from telegram.ext import ContextTypes


async def handle_text(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    if context.user_data.get('awaiting_transcription_title'):
        context.user_data['transcription_title'] = update.message.text

        context.user_data['awaiting_transcription_audio'] = True
        context.user_data['awaiting_transcription_title'] = False

        await update.message.reply_text("Отлично! Теперь отправьте аудиозапись.")

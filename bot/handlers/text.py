from telegram import Update
from telegram.ext import ContextTypes


async def handle_new_transcription_title(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    context.user_data['new_transcription_title'] = update.message.text

    context.user_data['awaiting_new_transcription_audio'] = True
    context.user_data['awaiting_new_transcription_title'] = False

    await update.message.reply_text("Отлично! Теперь отправьте аудиозапись для транскрибации:")


async def handle_text(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    if context.user_data.get('awaiting_new_transcription_title'):
        await handle_new_transcription_title(update, context)

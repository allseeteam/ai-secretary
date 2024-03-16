from typing import Dict, Callable

from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes


async def handle_my_transcriptions_callback(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    callback_query: CallbackQuery = update.callback_query
    await callback_query.answer()

    await callback_query.edit_message_text(text="Список ваших транскрипций: ...")


async def handle_add_transcription_callback(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    callback_query: CallbackQuery = update.callback_query
    await callback_query.answer()

    context.user_data['awaiting_transcription_title'] = True
    await callback_query.edit_message_text(text="Пожалуйста, введите название транскрипции.")


callback_handlers_mapping: Dict[str, Callable] = {
    'my_transcriptions': handle_my_transcriptions_callback,
    'add_transcription': handle_add_transcription_callback,
}


async def handle_callback_query(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    callback_query: CallbackQuery = update.callback_query
    callback_handler: Callable = callback_handlers_mapping.get(callback_query.data)

    if callback_handler:
        await callback_handler(update, context)
    else:
        await callback_query.answer()
        await callback_query.edit_message_text(text="Неизвестная команда.")

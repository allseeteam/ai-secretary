from typing import Dict, Callable, List

from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes
from markups import create_transcriptions_list_markup, create_main_menu_markup, create_transcription_menu_markup


async def handle_main_menu_callback(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id: int = update.effective_chat.id

    callback_query: CallbackQuery = update.callback_query
    await callback_query.answer()

    await context.bot.send_message(
        chat_id=chat_id,
        text="Привет! Чем я могу помочь?",
        reply_markup=create_main_menu_markup()
    )


async def handle_show_transcriptions_callback(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id: int = update.effective_chat.id

    callback_query: CallbackQuery = update.callback_query
    await callback_query.answer()

    await context.bot.send_message(
        chat_id=chat_id,
        text="Ваш список транскрипции.",
        reply_markup=create_transcriptions_list_markup(update, context)
    )


async def handle_add_transcription_callback(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    callback_query: CallbackQuery = update.callback_query
    await callback_query.answer()

    context.user_data['awaiting_transcription_title'] = True
    await callback_query.edit_message_text(text="Пожалуйста, введите название транскрипции.")


async def handle_transcription_menu_callback(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id: int = update.effective_chat.id

    callback_query: CallbackQuery = update.callback_query
    await callback_query.answer()

    await context.bot.send_message(
        chat_id=chat_id,
        text="Меню для транскрипции.",
        reply_markup=create_transcription_menu_markup(update, context)
    )


callback_handlers_mapping: Dict[str, Callable] = {
    'main_menu': handle_main_menu_callback,
    'show_transcriptions': handle_show_transcriptions_callback,
    'add_transcription': handle_add_transcription_callback,
    'transcription_menu': handle_transcription_menu_callback
}


async def handle_callback_query(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    callback_query: CallbackQuery = update.callback_query
    callback_data_parts: List[str] = callback_query.data.split(':')

    callback_key: str = callback_data_parts[0]
    callback_handler: Callable = callback_handlers_mapping.get(callback_key)

    if callback_handler:
        await callback_handler(update, context)
    else:
        await callback_query.answer()
        await callback_query.edit_message_text(text="Неизвестная команда.")

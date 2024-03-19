from typing import Dict, Callable, List

from database import get_transcription_text_by_id
from markups import create_done_transcriptions_menu_markup, create_main_menu_markup, create_transcription_menu_markup, create_transcription_text_menu_markup
from telegram import Update, CallbackQuery, InputFile
from telegram.ext import ContextTypes


async def handle_change_menu_main_callback(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    callback_query: CallbackQuery = update.callback_query
    await callback_query.answer()

    await callback_query.edit_message_text(
        text="Чем я могу помочь?",
        reply_markup=create_main_menu_markup()
    )


async def handle_change_menu_done_transcriptions_callback(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    callback_query: CallbackQuery = update.callback_query
    await callback_query.answer()

    await callback_query.edit_message_text(
        text="Список ваших транскрипций:",
        reply_markup=create_done_transcriptions_menu_markup(update, context)
    )


async def handle_scenario_add_transcription_start_callback(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id: int = update.effective_chat.id

    callback_query: CallbackQuery = update.callback_query
    await callback_query.answer()

    context.user_data['awaiting_new_transcription_title'] = True
    await context.bot.send_message(
        chat_id=chat_id,
        text="Давайте добавим вашу новую транскрипцию. Для начала введите её название:",
    )


async def handle_change_menu_transcription_callback(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    callback_query: CallbackQuery = update.callback_query
    await callback_query.answer()

    await callback_query.edit_message_text(
        text="Чем конкретно помочь с данной транскрипцией?",
        reply_markup=create_transcription_menu_markup(update, context)
    )


async def handle_change_menu_transcription_text_callback(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat_id: int = update.effective_chat.id
    callback_query: CallbackQuery = update.callback_query
    transcription_id: str = callback_query.data.split(":")[-1]

    transcription_text = get_transcription_text_by_id(transcription_id)

    await callback_query.answer()
    await callback_query.delete_message()

    document = InputFile(transcription_text, filename="transcription_text.txt")
    await context.bot.send_document(
        chat_id=chat_id,
        caption="Ваша транскрипция",
        document=document
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text="Чем ещё могу вам помочь с данной транскрипцией?",
        reply_markup=create_transcription_menu_markup(update, context)
    )


callback_handlers_mapping: Dict[str, Callable] = {
    'change_menu_main': handle_change_menu_main_callback,
    'change_menu_done_transcriptions': handle_change_menu_done_transcriptions_callback,
    'scenario_add_transcription_start': handle_scenario_add_transcription_start_callback,
    'change_menu_transcription': handle_change_menu_transcription_callback,
    'change_menu_transcription_text': handle_change_menu_transcription_text_callback
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
        await callback_query.edit_message_text(text="Пу-Пу")

import asyncio
import logging

from openai import OpenAI
from pydantic_settings import BaseSettings
from telegram import (
    Update,
    CallbackQuery
)
from telegram.ext import (
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
    CallbackQueryHandler
)

from database import get_transcription_text_by_id
from inline_keyboard_markups import (
    create_transcription_menu_markup_without_callback,
    create_stop_transcription_discussion_markup
)


class OpenAISettings(BaseSettings):
    openai_api_key: str

    class Config:
        env_file = 'env/.env.openai'


settings = OpenAISettings()
openai_client = OpenAI(api_key=settings.openai_api_key)
DISCUSSING_TRANSCRIPTION = 1


# noinspection PyUnusedLocal
async def start_transcription_discussion(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    global openai_client

    chat_id: int = update.effective_chat.id

    callback_query: CallbackQuery = update.callback_query
    transcription_id: str = callback_query.data.split(":")[-1]

    context.user_data['transcription_id'] = transcription_id

    await callback_query.answer()

    sticker_message = await context.bot.send_sticker(
        chat_id=chat_id,
        sticker='CAACAgIAAxkBAAJMS2YHPrVKVmiyNhVR3J5vQE2Qpu-kAAIjAAMoD2oUJ1El54wgpAY0BA'
    )

    try:
        transcripton_text: str = get_transcription_text_by_id(transcription_id)

        file_response = openai_client.files.create(
            file=transcripton_text.encode(),
            purpose='assistants'
        )
        file_id = file_response.id
        context.user_data['transcription_file_id'] = file_id

        context.user_data['transcripton_assistant'] = openai_client.beta.assistants.create(
            name=f"Transcription Assistant {transcription_id}",
            instructions=(
                "На основе текстовой транскрипции переговоров, сохраненной в прикрепленном файле, "
                "отвечай на все мои вопросы."
            ),
            tools=[{"type": "retrieval"}],
            file_ids=[file_id],
            model="gpt-4-turbo-preview",
        )

        context.user_data['transcription_thread'] = openai_client.beta.threads.create()

        await context.bot.delete_message(chat_id=chat_id, message_id=sticker_message.message_id)

        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "У вас есть вопросы по записи? "
                "Задавайте, и я подготовлю для вас краткую выжимку в нужном формате."
            ),
            reply_markup=create_stop_transcription_discussion_markup()
        )

        logging.info(f"User with id {chat_id} started transcription discussion")

        return DISCUSSING_TRANSCRIPTION

    except Exception as e:
        logging.error(f"Error starting transcription discussion: {e}")

        await context.bot.delete_message(chat_id=chat_id, message_id=sticker_message.message_id)

        await stop_transcription_discussion(update, context, is_error=True)


async def handle_transcription_discussion_user_message(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    global openai_client

    sticker_message = await update.message.reply_sticker(
        sticker='CAACAgIAAxkBAAJMS2YHPrVKVmiyNhVR3J5vQE2Qpu-kAAIjAAMoD2oUJ1El54wgpAY0BA'
    )

    try:
        message_text: str = update.message.text

        openai_client.beta.threads.messages.create(
            thread_id=context.user_data['transcription_thread'].id,
            role="user",
            content=message_text
        )

        run = openai_client.beta.threads.runs.create(
            thread_id=context.user_data['transcription_thread'].id,
            assistant_id=context.user_data['transcripton_assistant'].id,
        )

        while run.status in ['queued', 'in_progress', 'cancelling']:
            await asyncio.sleep(1)
            run = openai_client.beta.threads.runs.retrieve(
                thread_id=context.user_data['transcription_thread'].id,
                run_id=run.id
            )

        assistant_responce_text = (
            openai_client.beta.threads.messages.list(thread_id=context.user_data['transcription_thread'].id)
            .dict()['data'][0]['content'][0]['text']['value']
        )

        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=sticker_message.message_id)

        await (
            update
            .message
            .reply_text(
                text=assistant_responce_text,
                reply_markup=create_stop_transcription_discussion_markup()
            )
        )

        return DISCUSSING_TRANSCRIPTION

    except Exception as e:
        logging.error(f"Error while handling transcription discussion message: {e}")

        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=sticker_message.message_id)

        await stop_transcription_discussion(update, context, is_error=True)


# noinspection PyUnusedLocal
async def stop_transcription_discussion(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        is_error: bool = False
) -> int:
    global openai_client

    if not update.message:
        callback_query: CallbackQuery = update.callback_query
        await callback_query.answer()

    chat_id: int = update.effective_chat.id
    transcription_id: str = str(context.user_data['transcription_id'])

    sticker_message = await context.bot.send_sticker(
        chat_id=chat_id,
        sticker='CAACAgIAAxkBAAJMS2YHPrVKVmiyNhVR3J5vQE2Qpu-kAAIjAAMoD2oUJ1El54wgpAY0BA'
    )

    if context.user_data.get('transcripton_assistant'):
        try:
            openai_client.beta.assistants.delete(
                assistant_id=context.user_data['transcripton_assistant'].id
            )
        except Exception as e:
            logging.error(f"Error deleting transcription assistant: {e}. Maybe it never existed.")

    if context.user_data.get('transcription_thread'):
        try:
            openai_client.beta.threads.delete(
                thread_id=context.user_data['transcription_thread'].id
            )
        except Exception as e:
            logging.error(f"Error deleting transcription thread: {e}. Maybe it never existed.")

    if context.user_data.get('transcription_file_id'):
        try:
            openai_client.files.delete(file_id=context.user_data['transcription_file_id'])
        except Exception as e:
            logging.error(f"Error deleting transcription file: {e}. Maybe it never existed.")

    context.user_data.pop('transcription_id', None)
    context.user_data.pop('transcripton_assistant', None)
    context.user_data.pop('transcription_file_id', None)
    context.user_data.pop('transcription_thread', None)

    await context.bot.delete_message(chat_id=chat_id, message_id=sticker_message.message_id)

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            (
                "Произошла ошибка. Обсуждение было завершено. "
                if is_error
                else
                "Обсуждение завершено. "
            )
            +
            "Чем я могу ещё помочь?"
        ),
        reply_markup=create_transcription_menu_markup_without_callback(
            transcription_id=transcription_id
        )
    )

    logging.info(f"User with id {chat_id} stopped transcription discussion")

    return ConversationHandler.END


handle_discuss_transcription = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            start_transcription_discussion,
            pattern="^discuss_transcription:([^:]+)$"
        )
    ],
    states={
        DISCUSSING_TRANSCRIPTION: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & ~filters.Regex('^Закончить обсуждение$'),
                handle_transcription_discussion_user_message
            )
        ],
    },
    fallbacks=[
        CallbackQueryHandler(
            stop_transcription_discussion,
            pattern="^stop_transcription_discussion"
        )
    ]
)

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
from inline_keyboard_markups import create_transcription_menu_markup_without_callback
from reply_keyboard_markups import create_stop_transcription_discussion_markup


class OpenAISettings(BaseSettings):
    openai_api_key: str

    class Config:
        env_file = 'env/.env.openai'


settings = OpenAISettings()
openai_client = OpenAI(api_key=settings.openai_api_key)
DISCUSSING_TRANSCRIPTION = 1


# noinspection PyUnusedLocal
async def start_transcrition_discussion(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    global openai_client

    chat_id: int = update.effective_chat.id

    callback_query: CallbackQuery = update.callback_query
    transcription_id: str = callback_query.data.split(":")[-1]

    context.user_data['transcription_id'] = transcription_id

    await callback_query.answer()

    try:
        transcripton_text: str = get_transcription_text_by_id(transcription_id)
        context.user_data['transcripton_assistant'] = openai_client.beta.assistants.create(
            name=f"Transcription Assistant {transcription_id}",
            instructions=(
                "На основе данной текстовой транскрипции переговоров нескольких человек, отвечай на все мои вопросы:\n"
                f"```\n{transcripton_text}\n```"
            ),
            model="gpt-4-turbo-preview",
        )
        context.user_data['transcription_thread'] = openai_client.beta.threads.create()

        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "Давайте обсудим вашу транскрипцию. "
                "Вы можете задавать любые вопросы."
            ),
            reply_markup=create_stop_transcription_discussion_markup()
        )

        return DISCUSSING_TRANSCRIPTION

    except Exception as e:
        logging.error(f"Error starting transcription discussion: {e}")

        await stop_transcription_discussion(update, context)


async def handle_transcription_discussion_user_message(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    global openai_client

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

        await stop_transcription_discussion(update, context)


# noinspection PyUnusedLocal
async def stop_transcription_discussion(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    global openai_client

    chat_id: int = update.effective_chat.id
    transcription_id: str = str(context.user_data['transcription_id'])

    context.user_data.pop('message_count', None)
    context.user_data.pop('transcription_id', None)

    try:
        openai_client.beta.assistants.delete(
            assistant_id=context.user_data['transcripton_assistant'].id
        )
    except Exception as e:
        logging.error(f"Error deleting transcription assistant: {e}. Maybe it never existed.")

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "Чем я могу ещё помочь?"
        ),
        reply_markup=create_transcription_menu_markup_without_callback(
            transcription_id=transcription_id
        )
    )

    return ConversationHandler.END


handle_discuss_transcription = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            start_transcrition_discussion,
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
        MessageHandler(filters.Regex('^Закончить обсуждение$'), stop_transcription_discussion)
    ]
)

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

from inline_keyboard_markups import (
    create_transcription_menu_markup_without_callback,
    create_stop_transcription_discussion_markup
)


DISCUSSING_TRANSCRIPTION = 1


# noinspection PyUnusedLocal
async def start_transcrition_discussion(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    callback_query: CallbackQuery = update.callback_query
    transcription_id: str = callback_query.data.split(":")[-1]

    context.user_data['transcription_id'] = transcription_id

    await callback_query.answer()

    await callback_query.edit_message_text(
        text=(
            "Давайте обсудим вашу транскрипцию. "
            "Вы можете задавать любые вопросы."
        ),
        reply_markup=create_stop_transcription_discussion_markup()
    )

    return DISCUSSING_TRANSCRIPTION


async def handle_transcription_discussion_user_message(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    message_text: str = update.message.text

    if 'message_count' not in context.user_data:
        context.user_data['message_count'] = 0
    context.user_data['message_count'] += 1

    await (
        update
        .message
        .reply_text(
            text=(
                f"{message_text}\n\n"
                f"Всего сообщений: {context.user_data['message_count']}"
                "Мой ответ: ..."
            ),
            reply_markup=create_stop_transcription_discussion_markup()
        )
    )

    return DISCUSSING_TRANSCRIPTION


# noinspection PyUnusedLocal
async def stop_transcription_discussion(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    callback_query: CallbackQuery = update.callback_query
    await callback_query.answer()

    transcription_id: str = callback_query.data.split(":")[-1]
    chat_id: int = update.effective_chat.id

    context.user_data.pop('message_count', None)
    context.user_data.pop('transcription_id', None)

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
                filters.TEXT & ~filters.COMMAND,
                handle_transcription_discussion_user_message
            )
        ],
    },
    fallbacks=[
        CallbackQueryHandler(
            stop_transcription_discussion,
            pattern='^stop_transcription_discussion$'
        )
    ]
)

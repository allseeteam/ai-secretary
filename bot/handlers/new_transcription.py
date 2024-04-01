import logging

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

from database import add_transcription_to_db
from inline_keyboard_markups import (
    create_main_menu_markup,
    create_cancel_adding_new_transcription_markup
)


AWAITING_NEW_TRANSCRIPTION_TITLE = 1
AWAITING_NEW_TRANSCRIPTION_AUDIO_OR_VIDEO = 2


# noinspection PyUnusedLocal
async def request_new_transcription_title(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    chat_id: int = update.effective_chat.id

    callback_query: CallbackQuery = update.callback_query
    await callback_query.answer()

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "Как назовем вашу новую запись? "
            "Введите название, чтобы легко находить ее в списке сохраненных записей."
        ),
        reply_markup=create_cancel_adding_new_transcription_markup()
    )

    logging.info(f"Requesting new transcription title from {chat_id}")

    return AWAITING_NEW_TRANSCRIPTION_TITLE


async def handle_new_transcription_title(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    new_transcription_title: str = update.message.text
    context.user_data['new_transcription_title'] = new_transcription_title

    await update.message.reply_text(
        text=(
            "Отлично! "
            "Просто загрузите аудио или видео для обработки. "
            "Ваша информация попадет в очередь на транскрибацию!"
        ),
        reply_markup=create_cancel_adding_new_transcription_markup()
    )

    logging.info(f"Requesting new transcription audio or video from {update.effective_chat.id}")

    return AWAITING_NEW_TRANSCRIPTION_AUDIO_OR_VIDEO


async def add_new_transcription_and_end_conversation(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        file_type: str
) -> int:
    try:
        if file_type == "Audio":
            file_id: str = update.message.audio.file_id
        elif file_type == "Video":
            file_id: str = update.message.video.file_id
        else:
            raise Exception(f"Unknown file type: {file_type}")

        current_chat_id: int = update.effective_chat.id
        new_transcription_title: str = context.user_data.get('new_transcription_title', 'Без названия')

        add_transcription_to_db(
            chat_id=current_chat_id,
            title=new_transcription_title,
            uploaded_file_id=file_id,
            uploaded_file_type=file_type,
            status="Awaiting to filepath extraction"
        )

        await update.message.reply_text(
            text=(
                "🔄 Ваша запись добавлена в очередь на транскрибацию! "
                "Скоро вы получите текстовую версию и сможете задавать вопросы. "
                "Чем я могу ещё помочь?"
            ),
            reply_markup=create_main_menu_markup()
        )

        context.user_data.pop('new_transcription_title', None)

        logging.info(f"Added new transcription: {new_transcription_title} from {current_chat_id}")

        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text(
            text=(
                "Произошла ошибка при добавлении новой записи. "
                "Пожалуйста, повторите попытку позже."
            ),
            reply_markup=create_main_menu_markup()
        )

        context.user_data.pop('new_transcription_title', None)

        logging.error(f"Error adding new transcription: {e}")

        return ConversationHandler.END


async def handle_new_transcription_audio(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    return await add_new_transcription_and_end_conversation(
        update=update,
        context=context,
        file_type="Audio"
    )


async def handle_new_transcription_video(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    return await add_new_transcription_and_end_conversation(
        update=update,
        context=context,
        file_type="Video"
    )


# noinspection PyUnusedLocal
async def cancel_new_transcription(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    callback_query: CallbackQuery = update.callback_query
    await callback_query.answer()

    chat_id: int = update.effective_chat.id

    context.user_data.pop('new_transcription_title', None)

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "Процесс добавления записи отменен. "
            "Ваша информация останется без изменений. "
            "Чем я могу ещё помочь?"
        ),
        reply_markup=create_main_menu_markup()
    )

    logging.info(f"Cancelled new transcription from {chat_id}")

    return ConversationHandler.END


handle_add_new_transcription = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            request_new_transcription_title,
            pattern="^add_new_transcription$"
        )
    ],
    states={
        AWAITING_NEW_TRANSCRIPTION_TITLE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & ~filters.Regex('^Отмена$'),
                handle_new_transcription_title
            )
        ],
        AWAITING_NEW_TRANSCRIPTION_AUDIO_OR_VIDEO: [
            MessageHandler(
                filters.AUDIO,
                handle_new_transcription_audio
            ),
            MessageHandler(
                filters.VIDEO,
                handle_new_transcription_video
            )
        ]
    },
    fallbacks=[
        CallbackQueryHandler(
            cancel_new_transcription,
            pattern="^cancel_adding_new_transcription$"
        )
    ]
)

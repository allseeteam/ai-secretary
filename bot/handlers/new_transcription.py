from telegram import (
    Update,
    File,
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
from inline_keyboard_markups import create_main_menu_markup, create_cancel_adding_new_transcription_markup

AWAITING_NEW_TRANSCRIPTION_TITLE = 1
AWAITING_NEW_TRANSCRIPTION_AUDIO = 2


# noinspection PyUnusedLocal
async def request_new_transcription_title(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    callback_query: CallbackQuery = update.callback_query
    await callback_query.answer()

    await callback_query.edit_message_text(
        text=(
            "Давайте добавим вашу новую транскрипцию. "
            "Для начала введите её название:"
        ),
        reply_markup=create_cancel_adding_new_transcription_markup()
    )

    return AWAITING_NEW_TRANSCRIPTION_TITLE


async def handle_new_transcription_title(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    new_transcription_title: str = update.message.text
    context.user_data['new_transcription_title'] = new_transcription_title

    await (
        update
        .message
        .reply_text(
            text=(
                f"Отлично! "
                "Теперь отправьте аудиозапись для транскрибации:"
            ),
            reply_markup=create_cancel_adding_new_transcription_markup()
        )
    )

    return AWAITING_NEW_TRANSCRIPTION_AUDIO


async def handle_new_transcription_audio(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    new_transription_audio_file_id: str = update.message.audio.file_id
    current_chat_id: int = update.effective_chat.id

    new_transcription_title: str = context.user_data.get('new_transcription_title', 'Без названия')

    new_transcription_audio_file: File = await context.bot.get_file(new_transription_audio_file_id)
    new_transcription_audio_file_path: str = new_transcription_audio_file.file_path

    add_transcription_to_db(
        chat_id=current_chat_id,
        title=new_transcription_title,
        audio_file_path=new_transcription_audio_file_path,
        status="Awaiting upload to transcription API"
    )

    await (
        update
        .message
        .reply_text(
            text=(
                f"Ваша транскрипция '{new_transcription_title}' добавлена в очередь обработки. "
                "Чем я могу ещё помочь?"
            ),
            reply_markup=create_main_menu_markup()
        )
    )

    context.user_data.pop('new_transcription_title', None)

    return ConversationHandler.END


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
            "Добавление транскрипции отменено. "
            "Чем я могу ещё помочь?"
        ),
        reply_markup=create_main_menu_markup()
    )

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
                filters.TEXT & ~filters.COMMAND,
                handle_new_transcription_title
            )
        ],
        AWAITING_NEW_TRANSCRIPTION_AUDIO: [
            MessageHandler(
                filters.AUDIO,
                handle_new_transcription_audio
            )
        ]
    },
    fallbacks=[
        CallbackQueryHandler(
            cancel_new_transcription,
            pattern='^cancel_adding_new_transcription$'
        )
    ]
)

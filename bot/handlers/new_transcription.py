import logging
import os

from moviepy.editor import VideoFileClip
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
from inline_keyboard_markups import create_main_menu_markup
from reply_keyboard_markups import create_cancel_adding_new_transcription_markup


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
            "Давайте добавим вашу новую транскрипцию. "
            "Для начала введите её название."
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

    await update.message.reply_text(
            text=(
                f"Отлично! "
                "Теперь отправьте аудио или видеозапись для транскрибации."
            ),
            reply_markup=create_cancel_adding_new_transcription_markup()
        )

    return AWAITING_NEW_TRANSCRIPTION_AUDIO_OR_VIDEO


async def handle_new_transcription_audio(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    new_transription_audio_file_id: str = update.message.audio.file_id
    current_chat_id: int = update.effective_chat.id

    try:
        new_transcription_title: str = context.user_data.get('new_transcription_title', 'Без названия')

        new_transcription_audio_file: File = await context.bot.get_file(new_transription_audio_file_id)
        new_transcription_audio_file_path: str = new_transcription_audio_file.file_path

        add_transcription_to_db(
            chat_id=current_chat_id,
            title=new_transcription_title,
            audio_file_path=new_transcription_audio_file_path,
            status="Awaiting upload to transcription API"
        )

        await update.message.reply_text(
                text=(
                    f"Ваша транскрипция '{new_transcription_title}' добавлена в очередь обработки. "
                    "Чем я могу ещё помочь?"
                ),
                reply_markup=create_main_menu_markup()
            )

        context.user_data.pop('new_transcription_title', None)

        return ConversationHandler.END

    except Exception as e:
        logging.error(f"Error adding new transcription: {e}")

        await update.message.reply_text(
            text=(
                "Произошла ошибка при добавлении транскрипции. "
                "Пожалуйста, повторите попытку позже."
            ),
            reply_markup=create_main_menu_markup()
        )

        context.user_data.pop('new_transcription_title', None)

        return ConversationHandler.END


def extract_audio(video_path: str, audio_path: str) -> None:
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)

    with VideoFileClip(video_path) as video:
        video.audio.write_audiofile(audio_path, )


async def handle_new_transcription_video(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    new_transription_video_file_id: str = update.message.video.file_id
    current_chat_id: int = update.effective_chat.id

    try:
        new_transcription_title: str = context.user_data.get('new_transcription_title', 'Без названия')

        new_transcription_video_file: File = await context.bot.get_file(new_transription_video_file_id)
        new_transcription_video_file_path: str = new_transcription_video_file.file_path

        new_transcription_audio_file_path = "/".join(
            new_transcription_video_file_path.split("/")[:-2]
            +
            ["music", f"{new_transription_video_file_id}.mp3"]
        )

        extract_audio(new_transcription_video_file_path, new_transcription_audio_file_path)

        add_transcription_to_db(
            chat_id=current_chat_id,
            title=new_transcription_title,
            audio_file_path=new_transcription_audio_file_path,
            status="Awaiting upload to transcription API"
        )

        await update.message.reply_text(
                text=(
                    f"Ваша транскрипция '{new_transcription_title}' добавлена в очередь обработки. "
                    f"В скором времени она будет готова. "
                    "Чем я могу ещё помочь?"
                ),
                reply_markup=create_main_menu_markup()
            )

        context.user_data.pop('new_transcription_title', None)

        return ConversationHandler.END

    except Exception as e:
        logging.error(f"Error adding new transcription: {e}")

        await update.message.reply_text(
            text=(
                "Произошла ошибка при добавлении транскрипции. "
                "Пожалуйста, повторите попытку позже."
            ),
            reply_markup=create_main_menu_markup()
        )

        context.user_data.pop('new_transcription_title', None)

        return ConversationHandler.END


# noinspection PyUnusedLocal
async def cancel_new_transcription(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    chat_id: int = update.effective_chat.id

    context.user_data.pop('new_transcription_title', None)

    await update.message.reply_text(
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
        MessageHandler(filters.Regex('^Отмена$'), cancel_new_transcription)
    ]
)

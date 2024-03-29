import asyncio
import logging
import signal
from threading import Thread
from typing import Any

from pydantic_settings import BaseSettings
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler
)

from background_workers import (
    upload_any_files_to_transcription_api,
    fetch_any_transcription_from_api,
    extract_any_transcription_file_path_from_bot_server,
    extract_audio_from_any_transcription_video,
    notificate_any_transcription_status
)
from database import init_db
from handlers import (
    handle_start,
    handle_change_menu_callback_query,
    handle_add_new_transcription,
    handle_discuss_transcription
)


class AISecretaryTGBotSettings(BaseSettings):
    telegram_bot_token: str
    telegram_bot_api_base_url: str
    telegram_bot_read_timeout: int = 60
    telegram_bot_connect_timeout: int = 60

    class Config:
        env_file = 'env/.env.bot'


settings = AISecretaryTGBotSettings()
run_background_loops = True


# noinspection PyUnusedLocal
def signal_handler(signum: int, frame: Any) -> None:
    global run_background_loops
    run_background_loops = False


def setup_application() -> Application:
    application = (
        Application
        .builder()
        .token(settings.telegram_bot_token)
        .base_url(settings.telegram_bot_api_base_url)
        .read_timeout(settings.telegram_bot_read_timeout)
        .connect_timeout(settings.telegram_bot_connect_timeout)
        .build()
    )

    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(handle_add_new_transcription)
    application.add_handler(handle_discuss_transcription)
    application.add_handler(CallbackQueryHandler(handle_change_menu_callback_query))

    return application


def upload_files_to_transcription_api_loop():
    while run_background_loops:
        asyncio.run(upload_any_files_to_transcription_api())
        asyncio.run(asyncio.sleep(10))


def fetch_transcriptions_from_api_loop():
    while run_background_loops:
        asyncio.run(fetch_any_transcription_from_api())
        asyncio.run(asyncio.sleep(10))


async def save_transcription_file_path_from_bot_server_to_db_loop(application: Application):
    while run_background_loops:
        await extract_any_transcription_file_path_from_bot_server(application)
        await asyncio.sleep(10)


def extract_audio_from_any_transcription_video_loop():
    while run_background_loops:
        asyncio.run(extract_audio_from_any_transcription_video())
        asyncio.run(asyncio.sleep(10))


async def notificate_any_transcription_status_loop(application: Application):
    while run_background_loops:
        await notificate_any_transcription_status(application)
        await asyncio.sleep(10)


def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger().setLevel(logging.INFO)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logging.info("Setting up database...")
    init_db()

    logging.info("Starting background workers...")
    Thread(target=upload_files_to_transcription_api_loop, daemon=True).start()
    Thread(target=fetch_transcriptions_from_api_loop, daemon=True).start()
    Thread(target=extract_audio_from_any_transcription_video_loop, daemon=True).start()

    logging.info("Setting up application...")
    application = setup_application()

    logging.info("Starting background workers...")
    loop = asyncio.get_event_loop()
    loop.create_task(save_transcription_file_path_from_bot_server_to_db_loop(application))
    loop.create_task(notificate_any_transcription_status_loop(application))

    logging.info("Starting bot...")
    application.run_polling()


if __name__ == '__main__':
    main()

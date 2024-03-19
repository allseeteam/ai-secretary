import asyncio
import logging
import signal
from threading import Thread
from typing import Any

from pydantic_settings import BaseSettings
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from database import init_db
from handlers import handle_start, handle_callback_query, handle_audio, handle_text
from loop_workers import upload_any_files_to_transcription_api, fetch_any_transcription_from_api


class AISecretaryTGBotSettings(BaseSettings):
    telegram_bot_token: str
    telegram_bot_api_base_url: str
    telegram_bot_read_timeout: int = 60
    telegram_bot_connect_timeout: int = 60

    class Config:
        env_file = 'env/.env.bot'


settings = AISecretaryTGBotSettings()
run_background_loops = True


def signal_handler(signum: int, frame: Any) -> None:
    global run_background_loops
    run_background_loops = False


def setup_and_start_bot() -> None:
    application = (Application
                   .builder()
                   .token(settings.telegram_bot_token)
                   .base_url(settings.telegram_bot_api_base_url)
                   .read_timeout(settings.telegram_bot_read_timeout)
                   .connect_timeout(settings.telegram_bot_connect_timeout)
                   .build())
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    application.run_polling()


def upload_files_to_transcription_api_loop():
    while run_background_loops:
        asyncio.run(upload_any_files_to_transcription_api())
        asyncio.run(asyncio.sleep(10))


def fetch_transcriptions_from_api_loop():
    while run_background_loops:
        asyncio.run(fetch_any_transcription_from_api())
        asyncio.run(asyncio.sleep(10))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.getLogger().setLevel(logging.INFO)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logging.info("Setting up database...")
    init_db()

    logging.info("Starting background loops...")
    Thread(target=upload_files_to_transcription_api_loop, daemon=True).start()
    Thread(target=fetch_transcriptions_from_api_loop, daemon=True).start()

    logging.info("Starting bot...")
    setup_and_start_bot()

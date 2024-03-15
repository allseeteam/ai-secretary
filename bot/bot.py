from pydantic_settings import BaseSettings
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from handlers import start


class AISecretaryTGBotSettings(BaseSettings):
    telegram_bot_token: str
    telegram_bot_api_base_url: str
    telegram_bot_read_timeout: int = 60
    telegram_bot_connect_timeout: int = 60

    class Config:
        env_file = 'env/.env.bot'


def main() -> None:
    settings = AISecretaryTGBotSettings()
    application = (Application
                   .builder()
                   .token(settings.telegram_bot_token)
                   .base_url(settings.telegram_bot_api_base_url)
                   .read_timeout(settings.telegram_bot_read_timeout)
                   .connect_timeout(settings.telegram_bot_connect_timeout)
                   .build())
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.AUDIO, start))
    application.run_polling()


if __name__ == '__main__':
    main()

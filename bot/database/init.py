import sqlite3
from pydantic_settings import BaseSettings
import logging


class AISecretarySQLiteDBSettings(BaseSettings):
    sqlite_db_name: str = 'bot/database/ai-secretary.db'

    class Config:
        env_file = 'env/.env.sqlite'


def init_db(db_file) -> None:
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS users
        (chat_id INTEGER PRIMARY KEY, username TEXT)
        '''
    )
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS transcriptions
        (
        id INTEGER PRIMARY KEY,
        chat_id INTEGER, 
        audio_file_path TEXT, 
        status TEXT, 
        FOREIGN KEY(chat_id) REFERENCES users(chat_id)
        )
        '''
    )
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS transcription_texts
        (
        transcription_id INTEGER,
        full_text TEXT,
        FOREIGN KEY(transcription_id) REFERENCES transcriptions(id)
        )
        '''
    )
    conn.commit()
    conn.close()


def main() -> None:
    settings = AISecretarySQLiteDBSettings()
    init_db(settings.sqlite_db_name)
    logging.info(f'Database {settings.sqlite_db_name} initialized')


if __name__ == '__main__':
    main()

import sqlite3
from pydantic_settings import BaseSettings
import logging


class AISecretarySQLiteDBSettings(BaseSettings):
    sqlite_db_name: str = 'bot/database/ai-secretary.db'

    class Config:
        env_file = 'env/.env.sqlite'


def add_user_to_db(chat_id: int, username: str) -> None:
    settings = AISecretarySQLiteDBSettings()
    conn = sqlite3.connect(settings.sqlite_db_name)
    c = conn.cursor()
    c.execute(
        '''
        SELECT chat_id FROM users WHERE chat_id = ?
        ''',
        (chat_id,)
    )
    if c.fetchone() is None:
        c.execute(
            '''
            INSERT INTO users (chat_id, username) 
            VALUES (?, ?)
            ''',
            (chat_id, username)
        )
        conn.commit()
        logging.info(f'User {username} added to db')
    conn.close()

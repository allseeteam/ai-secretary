import logging
import sqlite3

from .db_connection import with_sqlite_connection


@with_sqlite_connection
def init_db(db_connection: sqlite3.Connection) -> None:
    cursor: sqlite3.Cursor = db_connection.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users
        (chat_id INTEGER PRIMARY KEY, username TEXT)
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS transcriptions
        (
        id INTEGER PRIMARY KEY,
        chat_id INTEGER, 
        title TEXT,
        audio_file_path TEXT, 
        status TEXT, 
        FOREIGN KEY(chat_id) REFERENCES users(chat_id)
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS transcription_texts
        (
        transcription_id INTEGER,
        full_text TEXT,
        FOREIGN KEY(transcription_id) REFERENCES transcriptions(id)
        )
        '''
    )

    db_connection.commit()
    logging.info(f'Database {settings.sqlite_db_name} initialized')

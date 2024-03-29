import sqlite3

from .db_connection import with_sqlite_connection


@with_sqlite_connection
def init_db(db_connection: sqlite3.Connection) -> None:
    cursor: sqlite3.Cursor = db_connection.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users
        (
        chat_id INTEGER PRIMARY KEY, 
        username TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS transcriptions
        (
        id INTEGER PRIMARY KEY,
        chat_id INTEGER, 
        title TEXT,
        uploaded_file_id TEXT,
        uploaded_file_type TEXT,
        video_file_path TEXT, 
        audio_file_path TEXT,
        status TEXT, 
        transcription_api_task_id TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
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
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(transcription_id) REFERENCES transcriptions(id)
        )
        '''
    )

    db_connection.commit()

import logging
import sqlite3
from typing import List

from .db_connection import with_sqlite_connection


@with_sqlite_connection
def add_transcription_to_db(
        db_connection: sqlite3.Connection,
        chat_id: int,
        title: str,
        audio_file_path: str,
        status: str
) -> int:
    cursor: sqlite3.Cursor = db_connection.cursor()

    cursor.execute(
        '''
        INSERT INTO transcriptions 
        (chat_id, title, audio_file_path, status) 
        VALUES (?, ?, ?, ?)
        ''',
        (chat_id, title, audio_file_path, status)
    )

    transcription_id = cursor.lastrowid

    db_connection.commit()
    logging.info(f'Transcription {title} added to db with id {transcription_id}')

    return transcription_id


@with_sqlite_connection
def update_transcription_status(
        db_connection: sqlite3.Connection,
        transcription_id: int,
        new_status: str
) -> None:
    cursor: sqlite3.Cursor = db_connection.cursor()

    cursor.execute(
        '''
        UPDATE transcriptions 
        SET status = ? 
        WHERE id = ?
        ''',
        (new_status, transcription_id))

    db_connection.commit()
    logging.info(f'Transcription {transcription_id} status updated to {new_status}')


@with_sqlite_connection
def get_user_transcriptions(
        db_connection: sqlite3.Connection,
        chat_id: int
) -> List[tuple]:
    cursor: sqlite3.Cursor = db_connection.cursor()

    cursor.execute(
        '''
        SELECT title 
        FROM transcriptions 
        WHERE chat_id = ?
        ''',
        (chat_id,)
    )

    user_transcriptions = cursor.fetchall()
    return user_transcriptions

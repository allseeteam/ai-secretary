import logging
import sqlite3

from .db_connection import with_sqlite_connection


@with_sqlite_connection
def add_transcription_text_to_db(
        db_connection: sqlite3.Connection,
        transcription_id: int,
        transcription_text_: str
) -> int:
    cursor: sqlite3.Cursor = db_connection.cursor()

    cursor.execute(
        '''
        INSERT INTO transcription_texts 
        (transcription_id, full_text) 
        VALUES (?, ?)
        ''',
        (transcription_id, transcription_text_)
    )

    transcription_text_id = cursor.lastrowid

    db_connection.commit()
    logging.info(f"Transcription text with id {transcription_text_id} for transcription {transcription_id} added to db")

    return transcription_text_id


@with_sqlite_connection
def get_transcription_text_by_id(
        db_connection: sqlite3.Connection,
        transcription_text_id: int
) -> str:
    cursor: sqlite3.Cursor = db_connection.cursor()

    cursor.execute(
        '''
        SELECT full_text
        FROM transcription_texts
        WHERE transcription_id = ?
        ''',
        (transcription_text_id,)
    )

    transcription_text = cursor.fetchone()[0]

    return transcription_text

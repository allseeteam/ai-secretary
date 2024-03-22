import logging
import sqlite3
from typing import (
    List,
    Any,
    Dict
)

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
    logging.info(f"Transcription {title} added to db with id {transcription_id}")

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
    logging.debug(f"Transcription {transcription_id} status updated to {new_status}")


@with_sqlite_connection
def get_user_transcriptions_with_given_status(
        db_connection: sqlite3.Connection,
        user_id: int,
        transcription_status: str
) -> List[tuple]:
    cursor: sqlite3.Cursor = db_connection.cursor()

    cursor.execute(
        '''
        SELECT id, title 
        FROM transcriptions 
        WHERE chat_id = ? AND status = ?
        ''',
        (user_id, transcription_status)
    )

    user_transcriptions_with_given_status = cursor.fetchall()
    logging.info(
        f"User with id {user_id} "
        f"fetched {len(user_transcriptions_with_given_status)} "
        f"transcriptions with status {transcription_status}"
    )

    return user_transcriptions_with_given_status


@with_sqlite_connection
def update_transcription_api_task_id(
        db_connection: sqlite3.Connection,
        transcription_id: int,
        transcription_api_task_id: str
) -> None:
    cursor: sqlite3.Cursor = db_connection.cursor()

    cursor.execute(
        '''
        UPDATE transcriptions
        SET transcription_api_task_id = ?
        WHERE id = ?
        ''',
        (transcription_api_task_id, transcription_id)
    )

    db_connection.commit()
    logging.debug(f"Transcription {transcription_id} API task ID updated to {transcription_api_task_id}")


@with_sqlite_connection
def get_transcription_details_by_status(
        db_connection: sqlite3.Connection,
        transcription_status: str,
        details_to_get: List[str]
) -> Dict[str, Any]:
    valid_fields = [
        'id',
        'chat_id',
        'title',
        'audio_file_path',
        'status',
        'transcription_api_task_id'
    ]

    valid_fields_to_get = [
        field
        for field in details_to_get
        if field in valid_fields
    ]

    valid_fields_to_get_str = ', '.join(valid_fields_to_get)
    if not valid_fields_to_get_str:
        raise ValueError("No valid fields provided for selection")

    cursor: sqlite3.Cursor = db_connection.cursor()

    query = f'''
        SELECT {valid_fields_to_get_str}
        FROM transcriptions
        WHERE status = ?
        LIMIT 1
    '''
    cursor.execute(query, (transcription_status,))

    row = cursor.fetchone()
    logging.debug(f"Transcription with status {transcription_status} details fetched: {row}")

    if row:
        return {field: value for field, value in zip(valid_fields_to_get, row)}
    else:
        return {}
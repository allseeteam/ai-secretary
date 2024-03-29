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
        uploaded_file_id: str,
        uploaded_file_type: str,
        status: str
) -> None:
    cursor: sqlite3.Cursor = db_connection.cursor()

    cursor.execute(
        '''
        INSERT INTO transcriptions 
        (chat_id, title, uploaded_file_id, uploaded_file_type, status) 
        VALUES (?, ?, ?, ?, ?)
        ''',
        (chat_id, title, uploaded_file_id, uploaded_file_type, status)
    )

    db_connection.commit()


@with_sqlite_connection
def get_transcription_details_by_id(
        db_connection: sqlite3.Connection,
        transcription_id: int,
        details_to_get: List[str]
) -> Dict[str, Any]:
    cursor: sqlite3.Cursor = db_connection.cursor()

    cursor.execute(
        f'''
        SELECT {", ".join(details_to_get)}
        FROM transcriptions
        WHERE id = ?
        ''',
        (transcription_id,)
    )

    transcription_details = cursor.fetchone()

    if transcription_details:
        return dict(zip(details_to_get, transcription_details))
    else:
        return {}


@with_sqlite_connection
def get_all_user_transcriptions_with_given_status(
        db_connection: sqlite3.Connection,
        user_id: int,
        transcription_status: str,
        details_to_get: List[str]
) -> List[Dict[str, Any]]:
    cursor: sqlite3.Cursor = db_connection.cursor()

    cursor.execute(
        f'''
        SELECT {", ".join(details_to_get)}
        FROM transcriptions 
        WHERE chat_id = ? AND status = ?
        ''',
        (user_id, transcription_status)
    )

    user_transcriptions_with_given_status = cursor.fetchall()

    if user_transcriptions_with_given_status:
        return [
            dict(zip(details_to_get, transcription_details))
            for transcription_details
            in user_transcriptions_with_given_status
        ]
    else:
        return []


@with_sqlite_connection
def get_details_for_any_transcription_with_given_status(
        db_connection: sqlite3.Connection,
        transcription_status: str,
        details_to_get: List[str]
) -> Dict[str, Any]:
    cursor: sqlite3.Cursor = db_connection.cursor()

    cursor.execute(
        f'''
        SELECT {", ".join(details_to_get)}
        FROM transcriptions
        WHERE status = ?
        LIMIT 1
        ''',
        (transcription_status,)
    )

    transcription_details = cursor.fetchone()

    if transcription_details:
        return dict(zip(details_to_get, transcription_details))
    else:
        return {}


@with_sqlite_connection
def update_transcription_details_by_id(
        db_connection: sqlite3.Connection,
        transcription_id: int,
        details_to_update: Dict[str, Any],
) -> None:
    cursor: sqlite3.Cursor = db_connection.cursor()

    cursor.execute(
        f'''
        UPDATE transcriptions
        SET {", ".join([f"{key} = ?" for key in details_to_update.keys()])}
        WHERE id = ?
        ''',
        tuple(details_to_update.values()) + (transcription_id,)
    )

    db_connection.commit()

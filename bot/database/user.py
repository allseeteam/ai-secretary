import logging
import sqlite3

from .db_connection import with_sqlite_connection


@with_sqlite_connection
def add_user_to_db(
        db_connection: sqlite3.Connection,
        chat_id: int,
        username: str
) -> None:
    cursor: sqlite3.Cursor = db_connection.cursor()

    cursor.execute(
        '''
        SELECT chat_id FROM users WHERE chat_id = ?
        ''',
        (chat_id,)
    )

    if cursor.fetchone() is None:
        cursor.execute(
            '''
            INSERT INTO users (chat_id, username) 
            VALUES (?, ?)
            ''',
            (chat_id, username)
        )

        db_connection.commit()
        logging.info(f"User {username} added to db")

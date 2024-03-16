import sqlite3
from functools import wraps
from typing import Any, Callable

from pydantic_settings import BaseSettings


class AISecretarySQLiteDBSettings(BaseSettings):
    sqlite_db_name: str = 'bot/database/ai-secretary.db'

    class Config:
        env_file = 'env/.env.sqlite'


db_settings = AISecretarySQLiteDBSettings()


def with_sqlite_connection(sqlite_func: Callable) -> Callable:
    @wraps(sqlite_func)
    def call_with_connection(*args, **kwargs):
        connection: sqlite3.Connection = sqlite3.connect(db_settings.sqlite_db_name)
        try:
            sqlite_func_result: Any = sqlite_func(connection, *args, **kwargs)
        finally:
            connection.close()
        return sqlite_func_result

    return call_with_connection

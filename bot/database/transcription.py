import sqlite3
from pydantic_settings import BaseSettings


class AISecretarySQLiteDBSettings(BaseSettings):
    sqlite_db_name: str = 'bot/database/ai-secretary.db'

    class Config:
        env_file = 'env/.env.sqlite'


def add_transcription_to_db(chat_id, title, audio_file_path, status):
    settings = AISecretarySQLiteDBSettings()
    conn = sqlite3.connect(settings.sqlite_db_name)
    c = conn.cursor()
    c.execute("INSERT INTO transcriptions (chat_id, title, audio_file_path, status) VALUES (?, ?, ?, ?)",
              (chat_id, title, audio_file_path, status))
    transcription_id = c.lastrowid
    conn.commit()
    conn.close()
    return transcription_id


def add_transcription_result(transcription_id, full_text):
    settings = AISecretarySQLiteDBSettings()
    conn = sqlite3.connect(settings.sqlite_db_name)
    c = conn.cursor()
    c.execute("INSERT INTO transcription_texts (transcription_id, full_text) VALUES (?, ?)",
              (transcription_id, full_text))
    conn.commit()
    conn.close()


def update_transcription_status(transcription_id, new_status):
    settings = AISecretarySQLiteDBSettings()
    conn = sqlite3.connect(settings.sqlite_db_name)
    c = conn.cursor()
    c.execute("UPDATE transcriptions SET status = ? WHERE id = ?", (new_status, transcription_id))
    conn.commit()
    conn.close()


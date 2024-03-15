import sqlite3


def add_user_to_db(chat_id, username):
    conn = sqlite3.connect('your_database.db')
    c = conn.cursor()

    # Проверка наличия пользователя в базе
    c.execute("SELECT chat_id FROM users WHERE chat_id = ?", (chat_id,))
    if c.fetchone() is None:
        # Добавление нового пользователя, если он не найден
        c.execute("INSERT INTO users (chat_id, username) VALUES (?, ?)", (chat_id, username))
        conn.commit()

    conn.close()
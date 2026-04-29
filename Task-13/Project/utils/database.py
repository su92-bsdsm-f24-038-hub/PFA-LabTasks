import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "db.sqlite3")


def get_connection():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        conn.commit()


def create_user(username, hashed_password):
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users(username, password) VALUES (?, ?)",
                (username, hashed_password),
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False


def get_user_by_username(username):
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, username, password FROM users WHERE username = ?",
            (username,),
        ).fetchone()


def save_chat(user_id, question, answer):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO chats(user_id, question, answer) VALUES (?, ?, ?)",
            (user_id, question, answer),
        )
        conn.commit()


def get_chat_history(user_id, limit=100):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, question, answer, timestamp
            FROM chats
            WHERE user_id = ?
            ORDER BY id ASC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

    return [
        {
            "id": row["id"],
            "question": row["question"],
            "answer": row["answer"],
            "timestamp": row["timestamp"],
        }
        for row in rows
    ]

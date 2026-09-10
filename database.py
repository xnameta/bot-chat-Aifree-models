import sqlite3
from datetime import datetime

DB = "bot.db"


def init_db():
    conn = sqlite3.connect(DB)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            model TEXT DEFAULT 'openai',
            created_at TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            content TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def ensure_user(user_id):
    conn = sqlite3.connect(DB)

    conn.execute("""
        INSERT OR IGNORE INTO users
        (user_id, model, created_at)
        VALUES (?, 'openai', ?)
    """, (user_id, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()


def get_model(user_id):
    conn = sqlite3.connect(DB)

    row = conn.execute(
        "SELECT model FROM users WHERE user_id=?",
        (user_id,)
    ).fetchone()

    conn.close()

    return row[0] if row else "openai"


def set_model(user_id, model):
    conn = sqlite3.connect(DB)

    conn.execute(
        "UPDATE users SET model=? WHERE user_id=?",
        (model, user_id)
    )

    conn.commit()
    conn.close()


def save_message(user_id, role, content):
    conn = sqlite3.connect(DB)

    conn.execute("""
        INSERT INTO messages
        (user_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        role,
        content,
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


def get_history(user_id, limit=20):
    conn = sqlite3.connect(DB)

    rows = conn.execute("""
        SELECT role, content
        FROM messages
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT ?
    """, (user_id, limit)).fetchall()

    conn.close()

    rows.reverse()

    return [
        {
            "role": role,
            "content": content
        }
        for role, content in rows
    ]


def clear_history(user_id):
    conn = sqlite3.connect(DB)

    conn.execute(
        "DELETE FROM messages WHERE user_id=?",
        (user_id,)
    )

    conn.commit()
    conn.close()
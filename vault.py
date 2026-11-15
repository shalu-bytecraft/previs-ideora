import sqlite3
import hashlib
import json
from datetime import datetime

DB_PATH = "ideora_vault.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS saved_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

def _hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register_user(username: str, password: str) -> tuple[bool, str]:
    username = username.strip().lower()
    if not username or not password:
        return False, "Please enter both a username and password."
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, _hash_pw(password)),
            )
        return True, "Account created! You're logged in."
    except sqlite3.IntegrityError:
        return False, "That username is already taken."

def login_user(username: str, password: str) -> bool:
    username = username.strip().lower()
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username = ?", (username,)
        ).fetchone()
    return bool(row and row[0] == _hash_pw(password))

def save_item(username: str, category: str, title: str, content):
    serialized = content if isinstance(content, str) else json.dumps(content)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO saved_items (username, category, title, content, created_at) VALUES (?, ?, ?, ?, ?)",
            (username, category, title, serialized, datetime.now().strftime("%b %d, %I:%M %p")),
        )

def get_items(username: str, category: str = None):
    with sqlite3.connect(DB_PATH) as conn:
        if category and category != "All":
            rows = conn.execute(
                "SELECT id, category, title, content, created_at FROM saved_items WHERE username = ? AND category = ? ORDER BY id DESC",
                (username, category),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, category, title, content, created_at FROM saved_items WHERE username = ? ORDER BY id DESC",
                (username,),
            ).fetchall()
    return rows

def delete_item(item_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM saved_items WHERE id = ?", (item_id,))
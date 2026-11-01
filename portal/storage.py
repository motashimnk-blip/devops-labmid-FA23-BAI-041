"""Saves submissions in a small SQLite database."""
import sqlite3
from datetime import datetime


def _connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path):
    with _connect(db_path) as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS submissions (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   reg_no TEXT NOT NULL,
                   title TEXT NOT NULL,
                   url TEXT NOT NULL,
                   submitted_at TEXT NOT NULL
               )"""
        )


def add_submission(db_path, data):
    with _connect(db_path) as conn:
        conn.execute(
            "INSERT INTO submissions (name, reg_no, title, url, submitted_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (data["name"], data["reg_no"], data["title"], data["url"],
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )


def list_submissions(db_path):
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM submissions ORDER BY id DESC").fetchall()
    return [dict(row) for row in rows]

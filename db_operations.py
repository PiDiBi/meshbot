import sqlite3
import threading
from datetime import datetime

thread_local = threading.local()


def get_db_connection():
    if not hasattr(thread_local, "connection"):
        thread_local.connection = sqlite3.connect("messages.db")
    return thread_local.connection


def initialize_database():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute(
        """CREATE TABLE IF NOT EXISTS message (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id INTEGER NOT NULL,
                    sender TEXT NOT NULL,
                    sender_short_name TEXT NOT NULL,
                    sender_long_name TEXT NOT NULL,
                    reply_id INTEGER NOT NULL,
                    channel INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    content TEXT NOT NULL
                );"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL
                );"""
    )
    conn.commit()
    print("Database schema initialized.")


def add_channel(name, url):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO channels (name, url) VALUES (?, ?)", (name, url))
    conn.commit()


def get_channels():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT name, url FROM channels")
    return c.fetchall()


def add_message(
    message_id,
    sender_id,
    sender_short_name,
    sender_long_name,
    reply_id,
    channel,
    content,
):
    conn = get_db_connection()
    c = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    c.execute(
        "INSERT INTO message (message_id, sender, sender_short_name, sender_long_name, reply_id, "
        "channel, date, content) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            message_id,
            sender_id,
            sender_short_name,
            sender_long_name,
            reply_id,
            channel,
            date,
            content,
        ),
    )
    return conn.commit()


def get_messages(top: int = 5):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, sender_short_name, sender_long_name, date, channel, "
        "content FROM message ORDER BY date DESC LIMIT ?",
        (top,),
    )
    return c.fetchall()

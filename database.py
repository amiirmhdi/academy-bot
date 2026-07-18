import sqlite3
import os

DB_NAME = "arakbot.db"

print("DB PATH:", os.path.abspath(DB_NAME))

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        chat_id INTEGER PRIMARY KEY,
        first_name TEXT,
        username TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tickets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        status TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER,
        sender TEXT,
        text TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_user(chat_id, first_name, username):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    INSERT OR IGNORE INTO users(chat_id,first_name,username)
    VALUES(?,?,?)
    """, (chat_id, first_name, username))

    conn.commit()
    conn.close()


def get_all_users():

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT chat_id FROM users")

    users = cur.fetchall()

    conn.close()

    return users


def get_open_ticket(user_id):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    SELECT id FROM tickets
    WHERE user_id=? AND status='open'
    """, (user_id,))

    ticket = cur.fetchone()

    conn.close()

    return ticket


def create_ticket(user_id):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO tickets(user_id,status)
    VALUES(?,?)
    """, (user_id, "open"))

    conn.commit()

    ticket_id = cur.lastrowid

    conn.close()

    return ticket_id


def close_ticket(user_id):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    UPDATE tickets
    SET status='closed'
    WHERE user_id=? AND status='open'
    """, (user_id,))

    conn.commit()
    conn.close()


def save_message(ticket_id, sender, text):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO messages(ticket_id, sender, text)
    VALUES(?,?,?)
    """, (ticket_id, sender, text))

    conn.commit()
    conn.close()

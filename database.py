import psycopg2
from config import DATABASE_URL


def get_connection():

    print("DATABASE_URL =", DATABASE_URL)

    return psycopg2.connect(DATABASE_URL)


def init_db():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        chat_id BIGINT PRIMARY KEY,
        first_name TEXT,
        username TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tickets(
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        status TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id SERIAL PRIMARY KEY,
        ticket_id INTEGER,
        sender TEXT,
        text TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ratings(
        chat_id BIGINT PRIMARY KEY,
        first_name TEXT,
        username TEXT,
        rating INTEGER,
        review TEXT DEFAULT ''
    );
    """)

    conn.commit()

    cur.close()
    conn.close()


def add_user(chat_id, first_name, username):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO users(chat_id, first_name, username)
    VALUES (%s,%s,%s)
    ON CONFLICT(chat_id)
    DO NOTHING;
    """,(chat_id,first_name,username))

    conn.commit()

    cur.close()
    conn.close()


def get_all_users():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT chat_id
    FROM users
    """)

    users = cur.fetchall()

    cur.close()
    conn.close()

    return users


def get_open_ticket(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id
    FROM tickets
    WHERE user_id=%s
    AND status='open'
    """, (user_id,))

    ticket = cur.fetchone()

    cur.close()
    conn.close()

    return ticket


def create_ticket(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO tickets(user_id,status)
    VALUES(%s,%s)
    RETURNING id
    """, (user_id, "open"))

    ticket_id = cur.fetchone()[0]

    conn.commit()

    cur.close()
    conn.close()

    return ticket_id


def close_ticket(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE tickets
    SET status='closed'
    WHERE user_id=%s
    AND status='open'
    """, (user_id,))

    conn.commit()

    cur.close()
    conn.close()


def save_message(ticket_id, sender, text):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO messages(ticket_id, sender, text)
    VALUES (%s, %s, %s)
    """, (ticket_id, sender, text))

    conn.commit()

    cur.close()
    conn.close()    


def get_users_count():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")

    count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return count


def get_first_user():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT chat_id, first_name, username
    FROM users
    ORDER BY chat_id ASC
    LIMIT 1
    """)

    user = cur.fetchone()

    cur.close()
    conn.close()

    return user


def get_last_user():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT chat_id, first_name, username
    FROM users
    ORDER BY chat_id DESC
    LIMIT 1
    """)

    user = cur.fetchone()

    cur.close()
    conn.close()

    return user


def get_users_info():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT chat_id, first_name, username
    FROM users
    ORDER BY chat_id
    """)

    users = cur.fetchall()

    cur.close()
    conn.close()

    return users


def save_rating(chat_id, first_name, username, rating):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO ratings(chat_id, first_name, username, rating)
    VALUES(%s,%s,%s,%s)
    ON CONFLICT(chat_id)
    DO UPDATE SET
    first_name=EXCLUDED.first_name,
    username=EXCLUDED.username,
    rating=EXCLUDED.rating;
    """, (chat_id, first_name, username, rating))

    conn.commit()

    cur.close()
    conn.close()


def save_review(chat_id, review):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE ratings
    SET review=%s
    WHERE chat_id=%s
    """, (review, chat_id))

    conn.commit()

    cur.close()
    conn.close()


def get_rating_stats():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        COUNT(*),
        COALESCE(AVG(rating),0)
    FROM ratings
    """)

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result

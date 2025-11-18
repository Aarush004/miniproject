import psycopg2.extras
from .database import get_db_connection

def add_user(username: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING id", (username,))
        user_id = cur.fetchone()["id"]
        conn.commit()
        return user_id
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        return cur.fetchone()["id"]
    finally:
        cur.close()
        conn.close()

def get_topics_mastery(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT topic, mastery_prob FROM topic_mastery WHERE user_id=%s", (user_id,))
    data = {r["topic"]: r["mastery_prob"] for r in cur.fetchall()}
    cur.close()
    conn.close()
    return data

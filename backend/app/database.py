import psycopg2
import psycopg2.extras
from .config import DATABASE_URL

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # Users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL
        )
    ''')

    # Topic mastery tracking
    cur.execute('''
        CREATE TABLE IF NOT EXISTS topic_mastery (
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            topic TEXT NOT NULL,
            status TEXT NOT NULL,
            mastery_prob REAL DEFAULT 0.0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, topic)
        )
    ''')

    # KT history log (optional)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS kt_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            topic TEXT NOT NULL,
            correct BOOLEAN,
            old_prob REAL,
            new_prob REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    cur.close()
    conn.close()
    print("✅ PostgreSQL database initialized.")

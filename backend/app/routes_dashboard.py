from fastapi import APIRouter
from .database import get_db_connection

router = APIRouter()

@router.get("/dashboard/mastery/{user_id}")
def get_mastery(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT topic, mastery_prob, last_updated FROM topic_mastery WHERE user_id=%s", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"topic": r[0], "mastery": float(r[1]), "last_updated": r[2]}
        for r in rows
    ]

@router.get("/dashboard/history/{user_id}/{topic}")
def get_kt_history(user_id: int, topic: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT timestamp, old_prob, new_prob, correct 
        FROM kt_history 
        WHERE user_id=%s AND topic=%s
        ORDER BY timestamp ASC
    """, (user_id, topic))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"timestamp": r[0], "old": float(r[1]), "new": float(r[2]), "correct": r[3]}
        for r in rows
    ]

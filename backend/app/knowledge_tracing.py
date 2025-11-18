import math
from .database import get_db_connection

# parameters
LEARN_RATE = 0.3   # how fast user learns when correct
FORGET_RATE = 0.1  # how fast they forget when wrong

def update_mastery_probability(user_id: int, topic: str, correct: bool):
    """
    Bayesian-style mastery update: increases or decreases mastery probability.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch current mastry probability
    cur.execute("SELECT mastery_prob FROM topic_mastery WHERE user_id=%s AND topic=%s", (user_id, topic))
    row = cur.fetchone()
    current_prob = row[0] if row else 0.2  # start low if unseen

    # Udate rule
    if correct:
        new_prob = current_prob + (1 - current_prob) * LEARN_RATE
    else:
        new_prob = current_prob * (1 - FORGET_RATE)

    new_prob = round(new_prob, 3)

    # Upsert updated probabilty
    cur.execute('''
        INSERT INTO topic_mastery (user_id, topic, status, mastery_prob)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id, topic)
        DO UPDATE SET mastery_prob = EXCLUDED.mastery_prob, last_updated = CURRENT_TIMESTAMP
    ''', (user_id, topic, 'in_progress', new_prob))

    # Log kT history
    cur.execute('''
        INSERT INTO kt_history (user_id, topic, correct, old_prob, new_prob)
        VALUES (%s, %s, %s, %s, %s)
    ''', (user_id, topic, correct, current_prob, new_prob))

    conn.commit()
    cur.close()
    conn.close()
    return new_prob
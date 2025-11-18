import traceback
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .ollama_client import chat_with_ollama, detect_topic_with_llm
from .database import init_db, get_db_connection
from . import crud
from .knowledge_tracing import update_mastery_probability
from .schemas import ChatRequest, ChatResponse, UserCreate

# Dashboard router
from .routes_dashboard import router as dashboard_router


# ---------------------------------------------------
# FASTAPI APP
# ---------------------------------------------------
app = FastAPI(title="EduBuddy with Knowledge Tracing (PostgreSQL + FastAPI)")

# Include dashboard routes
app.include_router(dashboard_router, prefix="/api")


# ---------------------------------------------------
# CORS
# ---------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------
# Initialize DB
# ---------------------------------------------------
init_db()


# ---------------------------------------------------
# System Prompt
# ---------------------------------------------------
SYSTEM_PROMPT = """
You are EduBuddy — a friendly, patient, and knowledgeable AI coding tutor.

Rules:
1. Respond only to programming or computer science topics.
2. Explain step by step in simple language.
3. Include exactly one short code example in every reply.
4. Adapt to the student's skill level.
5. If topic is irrelevant, respond: "I can only help with programming-related questions."
"""


# ---------------------------------------------------
# Health Endpoint
# ---------------------------------------------------
@app.get("/api/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------
# Create User
# ---------------------------------------------------
@app.post("/users")
def create_user(payload: UserCreate):
    user_id = crud.add_user(payload.username)
    return {"user_id": user_id, "username": payload.username}


# ---------------------------------------------------
# Chat Endpoint
# ---------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    try:
        mastery = crud.get_topics_mastery(payload.user_id)
        mastery_summary = ", ".join([f"{t}: {p:.2f}" for t, p in mastery.items()]) or "no mastery data"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + f" Current mastery: {mastery_summary}."},
            {"role": "user", "content": payload.message},
        ]

        print("\nSTEP 1: Sending request to Ollama...")
        reply = chat_with_ollama(messages)
        print("STEP 2: Reply received.")

        topic = detect_topic_with_llm(payload.message)
        correct = random.choice([True, False])
        print(f"STEP 3: Updating KT → topic={topic}, correct={correct}")

        new_prob = update_mastery_probability(payload.user_id, topic, correct)
        print(f"STEP 4: Mastery updated → {new_prob:.2f}")

        return {
            "reply": (
                f"{reply}\n\n"
                f"[Knowledge Tracing] Topic: {topic} | Correct: {correct} | New Mastery: {new_prob:.2f}"
            )
        }

    except Exception as e:
        print("ERROR in /chat:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------
# Get Mastery Overview
# ---------------------------------------------------
@app.get("/mastery/{user_id}")
def get_mastery(user_id: int):
    try:
        mastery = crud.get_topics_mastery(user_id)
        return {"mastery": mastery}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------
# Get Full KT History
# ---------------------------------------------------
@app.get("/mastery/history/{user_id}")
def get_mastery_history(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT topic, correct, old_prob, new_prob, timestamp
            FROM kt_history
            WHERE user_id = %s
            ORDER BY timestamp ASC
            """,
            (user_id,),
        )
        rows = cur.fetchall()

        data = [
            {
                "topic": r[0],
                "correct": r[1],
                "old_prob": r[2],
                "new_prob": r[3],
                "timestamp": r[4].isoformat(),
            }
            for r in rows
        ]

        return {"history": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cur.close()
        conn.close()

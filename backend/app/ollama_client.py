import requests
from .config import OLLAMA_BASE, OLLAMA_MODEL

def chat_with_ollama(messages, stream=False, temperature=0.7, max_tokens=512):
    """
    Sends chat messages to Ollama’s local /api/chat endpoint.
    Example message format:
        [{"role": "system", "content": "You are helpful"}, {"role": "user", "content": "Hello"}]
    """
    url = f"{OLLAMA_BASE}/api/chat"
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": stream,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    response = requests.post(url, json=payload, timeout=500)
    response.raise_for_status()
    data = response.json()
    # Handle both typical shapes of Ollama responses
    if isinstance(data, dict):
        if "message" in data and "content" in data["message"]:
            return data["message"]["content"].strip()
        elif "choices" in data:
            return data["choices"][0]["message"]["content"].strip()
        elif "text" in data:
            return data["text"].strip()
    return str(data)
def detect_topic_with_llm(user_question: str) -> str:
    """
    Uses Ollama (Llama 3.2) to infer which topic the question belongs to.
    Returns a concise topic name, e.g. 'Algorithms: Cyclic Sort'.
    """
    url = f"{OLLAMA_BASE}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": (
            "You are a topic classifier for a tutoring system.\n"
            "Given the student's question below, identify the most relevant learning topic.\n"
            "Return ONLY the topic name in this format: <Category>: <Specific Concept>.\n\n"
            f"Question: {user_question}"
        ),
        "stream": False
    }
    try:
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        # Ollama sometimes returns {"response": "..."} or {"output": "..."}
        topic = (
            data.get("response")
            or data.get("output")
            or data.get("text")
            or "General: Miscellaneous"
        )
        return topic.strip()
    except Exception as e:
        print(f"⚠️ Topic detection failed: {e}")
        return "General: Miscellaneous"
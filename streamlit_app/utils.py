import requests

BASE_URL = "http://localhost:8000/api"

def fetch_mastery(user_id):
    return requests.get(f"{BASE_URL}/dashboard/mastery/{user_id}").json()

def fetch_history(user_id, topic):
    return requests.get(f"{BASE_URL}/dashboard/history/{user_id}/{topic}").json()

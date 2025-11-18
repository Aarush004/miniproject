import streamlit as st
import requests

BASE_URL = "http://localhost:8000"

st.title("GenAI Learning Tutor")

user_id = st.number_input("Enter User ID", min_value=1, step=1)
topic = st.text_input("Topic")
message = st.text_area("Question to send to tutor")

if st.button("Submit"):
    payload = {"user_id": user_id, "message": message}

    try:
        res = requests.post(f"{BASE_URL}/chat", json=payload)
        
        if res.status_code == 200:
            st.success("Response received:")
            st.write(res.json()["reply"])
        else:
            st.error(f"Backend error: {res.status_code} -> {res.text}")

    except Exception as e:
        st.error("Error communicating with backend")
        st.write(str(e))

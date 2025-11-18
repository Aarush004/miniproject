import streamlit as st
import pandas as pd
import plotly.express as px
from utils import fetch_mastery, fetch_history

st.title("📊 Knowledge Tracing Dashboard")

user_id = st.number_input("Enter User ID", min_value=1, step=1)

if user_id:
    mastery = fetch_mastery(user_id)

    if mastery:
        df_mastery = pd.DataFrame(mastery)

        st.subheader("Topic Mastery Overview")
        st.bar_chart(df_mastery.set_index("topic")["mastery"])

        topic = st.selectbox("Select a topic to view history", df_mastery["topic"])

        if topic:
            history = fetch_history(user_id, topic)
            df_hist = pd.DataFrame(history)

            fig = px.line(df_hist, x="timestamp", y="new", title=f"Mastery Trend — {topic}")
            st.plotly_chart(fig)

            st.write("Raw history data:")
            st.dataframe(df_hist)

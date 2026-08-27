import streamlit as st
from mock_data import get_messages

st.title("📊 Customer Intelligence Dashboard")

df = get_messages()

total = len(df)
positive = len(df[df["sentiment"] == "Positive"])
negative = len(df[df["sentiment"] == "Negative"])

col1, col2, col3 = st.columns(3)

col1.metric("Total Messages", total)
col2.metric("Positive", positive)
col3.metric("Negative", negative)

st.subheader("Recent Messages")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

queue_counts = df["queue"].value_counts()

st.subheader("Messages by Queue")

st.bar_chart(queue_counts)

sentiment_counts = df["sentiment"].value_counts()

st.subheader("Sentiment Distribution")

st.bar_chart(sentiment_counts)
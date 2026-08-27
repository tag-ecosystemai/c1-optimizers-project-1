import streamlit as st
from mock_data import get_messages

st.title("👥 Team Queues")

df = get_messages()

queues = df["queue"].unique()

selected_queue = st.selectbox(
    "Select Team Queue",
    queues
)

team_messages = df[
    df["queue"] == selected_queue
]

st.subheader(f"{selected_queue} Queue")

st.dataframe(
    team_messages,
    use_container_width=True,
    hide_index=True
)
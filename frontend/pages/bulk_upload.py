import streamlit as st
import pandas as pd

st.title("📁 Bulk Message Classification")

uploaded_file = st.file_uploader(
    "Upload customer messages CSV",
    type=["csv"]
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    st.subheader("Uploaded Data")

    st.dataframe(
        df,
        use_container_width=True
    )

    if st.button("Process Messages"):

        st.success(
            f"{len(df)} messages ready for classification."
        )
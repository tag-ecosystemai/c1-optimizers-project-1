import streamlit as st


st.title("💬 Classify Customer Message")

st.caption(
    "Submit a customer message to classify intent, sentiment, "
    "language and routing queue."
)

st.divider()

# --------------------------------
# Message Input
# --------------------------------

message = st.text_area(
    "Customer Message",
    placeholder=(
        "Example: I haven't received my refund yet "
        "and it has been two weeks."
    ),
    height=180,
)

st.caption("Supported languages: 🇬🇧 English · 🇩🇪 German")

# --------------------------------
# Classify Button
# --------------------------------

if st.button(
    "🔍 Classify Message",
    type="primary",
    use_container_width=True,
):

    if not message.strip():

        st.warning("Please enter a customer message.")

    else:

        # Temporary mock classification
        intent = "Refund"
        sentiment = "Negative"
        language = "English"
        confidence = "94%"
        queue = "Billing Team"

        st.success("Message classified successfully!")

        st.divider()

        # --------------------------------
        # Prediction Cards
        # --------------------------------

        st.subheader("📊 Classification Results")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Intent",
                intent,
            )

        with col2:
            st.metric(
                "Sentiment",
                f"🔴 {sentiment}",
            )

        with col3:
            st.metric(
                "Language",
                f"🇬🇧 {language}",
            )

        with col4:
            st.metric(
                "Confidence",
                confidence,
            )

        st.divider()

        # --------------------------------
        # Routing
        # --------------------------------

        st.subheader("🚦 Automatic Routing")

        st.info(
            f"✓ This message has been automatically routed "
            f"to the **{queue}**."
        )

        # --------------------------------
        # Message Details
        # --------------------------------

        with st.expander("📄 View Original Message"):

            st.write(message)

        # --------------------------------
        # Classification Summary
        # --------------------------------

        st.subheader("🧠 Classification Summary")

        st.write(
            f"""
            The system identified this message as a
            **{intent}** issue with **{sentiment.lower()} sentiment**.

            The detected language is **{language}**, and the model
            classified the message with a confidence score of
            **{confidence}**.

            Based on the predicted intent, the message was routed
            to the **{queue}**.
            """
        )
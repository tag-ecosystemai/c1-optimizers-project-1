
import streamlit as st

# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------
st.set_page_config(
    page_title="Customer Intelligence Classifier",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# Custom Styling
# ---------------------------------------------------
st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Hero Section */

.hero {
    padding: 2.5rem;
    border-radius: 20px;
    background: linear-gradient(135deg,#0f172a,#1e293b);
    color: white;
    margin-bottom: 2rem;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 0.5rem;
}

.hero p {
    font-size: 1.15rem;
    color: #e2e8f0;
}

/* Feature cards */

.feature-card {
    padding: 1.5rem;
    border-radius: 15px;
    border: 1px solid var(--secondary-background-color);
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    min-height: 180px;

    /* Shadow */
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);

    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.feature-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.18);
}

.feature-card h3 {
    color: var(--text-color);
    margin-bottom: 0.8rem;
}

.feature-card p,
.feature-card li {
    color: var(--text-color);
}

/* Workflow */

.workflow {
    padding: 1.2rem;
    border-radius: 12px;
    border: 1px solid var(--secondary-background-color);
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    text-align: center;
    font-weight: 600;

    /* Shadow */
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.10);

    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.workflow:hover {
    transform: translateY(-3px);
    box-shadow: 0 7px 16px rgba(0, 0, 0, 0.16);
}

.footer {
    text-align: center;
    color: gray;
    margin-top: 3rem;
    font-size: 0.9rem;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------
with st.sidebar:

    st.title("🎯 Team Optimizers")

    st.caption("Customer Intelligence Platform")

    st.divider()

    st.markdown("""
    ### Navigation

    Use the pages below to interact with the platform.
    """)

    st.divider()

    st.success("🟢 System Ready")

    st.caption("AI-powered customer support intelligence")


# ---------------------------------------------------
# HERO
# ---------------------------------------------------

st.markdown("""
<div class="hero">

<h1>Customer Intelligence Classifier</h1>

<p>
An intelligent customer support platform that automatically classifies
customer messages by intent and sentiment, detects language,
routes messages to the appropriate specialist team,
and provides actionable analytics through an interactive dashboard.
</p>

</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# Overview
# ---------------------------------------------------

st.subheader("Welcome 👋")

st.write("""
This application helps customer support teams efficiently manage incoming
customer messages using Artificial Intelligence.

Every message is analyzed to identify **what the customer needs**, 
**how the customer feels**, and **which team should handle the request**.
""")


# ---------------------------------------------------
# System Highlights
# ---------------------------------------------------

st.subheader("Platform Capabilities")

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("""
    <div class="feature-card">

    <h3>💬 Smart Classification</h3>

    Automatically identify the customer's intent such as:

    • Refund

    • Technical Support

    • Account Access

    • Payment Issues

    • Order Status

    </div>
    """, unsafe_allow_html=True)


with col2:

    st.markdown("""
    <div class="feature-card">

    <h3>😊 Sentiment Analysis</h3>

    Detect whether a customer message expresses:

    🟢 Positive sentiment

    🔴 Negative sentiment

    Helping support teams prioritize unhappy customers faster.

    </div>
    """, unsafe_allow_html=True)


with col3:

    st.markdown("""
    <div class="feature-card">

    <h3>🌍 Multilingual Support</h3>

    The platform supports both:

    🇬🇧 English

    🇩🇪 German

    Messages are automatically detected and classified regardless of language.

    </div>
    """, unsafe_allow_html=True)


st.write("")

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("""
    <div class="feature-card">

    <h3>🚦 Intelligent Routing</h3>

    Once an intent is predicted, the message is automatically routed to the correct queue.

    Example:

    Refund → Billing Team

    Login Issue → Account Support

    </div>
    """, unsafe_allow_html=True)


with col2:

    st.markdown("""
    <div class="feature-card">

    <h3>📁 Bulk Processing</h3>

    Upload hundreds or thousands of customer messages using CSV files.

    The system processes and classifies them efficiently for backlog management.

    </div>
    """, unsafe_allow_html=True)


with col3:

    st.markdown("""
    <div class="feature-card">

    <h3>📊 Business Intelligence</h3>

    Visual dashboards provide insights into:

    • Message volume

    • Queue workload

    • Sentiment trends

    • Language distribution

    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------
# Workflow
# ---------------------------------------------------

st.divider()

st.subheader("How The System Works")

st.write("""
The entire platform follows a simple intelligent workflow from message
ingestion to team routing and business analytics.
""")

st.write("")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
    <div class="workflow">
    📩<br>
    Customer Message
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="workflow">
    🧠<br>
    AI Classification
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="workflow">
    😊<br>
    Sentiment + Language
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="workflow">
    🚦<br>
    Queue Routing
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="workflow">
    📊<br>
    Dashboard Insights
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------
# Navigation Guide
# ---------------------------------------------------

st.divider()

st.subheader("Explore The Platform")

left, right = st.columns(2)

with left:

    st.markdown("### 🏠 Dashboard")

    st.write("""
    Monitor customer support activity through interactive analytics including:

    - Total customer messages
    - Message volume over time
    - Queue distribution
    - Sentiment trends
    - Language insights
    """)

    st.markdown("### 💬 Classify Message")

    st.write("""
    Submit a single customer message and instantly receive:

    - Intent prediction
    - Sentiment classification
    - Detected language
    - Assigned queue
    - Confidence score
    """)


with right:

    st.markdown("### 📁 Bulk Upload")

    st.write("""
    Upload CSV files containing customer support messages.

    The system will classify every message and allow the processed
    results to be downloaded for further analysis.
    """)

    st.markdown("### 👥 Team Queues")

    st.write("""
    Each specialist team can view only the messages routed to them.

    This demonstrates intelligent routing and creates a realistic
    customer support workflow.
    """)


# ---------------------------------------------------
# Supported Queues
# ---------------------------------------------------

st.divider()

st.subheader("Specialist Support Queues")

queue1, queue2, queue3 = st.columns(3)

with queue1:

    st.info("""
    💳 **Billing**

    Refunds

    Payment Issues

    Billing enquiries
    """)

with queue2:

    st.info("""
    🛠 **Technical Support**

    Application issues

    System errors

    Feature assistance
    """)

with queue3:

    st.info("""
    👤 **Account Support**

    Login problems

    Password reset

    Account access
    """)


queue4, queue5 = st.columns(2)

with queue4:

    st.info("""
    📦 **Order Management**

    Delivery tracking

    Order status

    Shipping enquiries
    """)

with queue5:

    st.info("""
    🔄 **Customer Retention**

    Subscription cancellation

    Account cancellation

    Retention requests
    """)


# ---------------------------------------------------
# About
# ---------------------------------------------------

st.divider()

st.subheader("Project Objective")

st.write("""
The Customer Intelligence Classifier was designed to help organizations
automatically analyze customer support messages and improve operational
efficiency through intelligent classification, sentiment detection,
automatic routing, multilingual support, and real-time analytics.

This Streamlit application serves as the user-facing interface connecting
customer interactions with the AI classification backend and operational
support teams.
""")


# ---------------------------------------------------
# Footer
# ---------------------------------------------------

st.markdown("""
<div class="footer">

Built by <b>Team Optimizers</b> • Customer Intelligence Classifier

Streamlit Frontend

</div>
""", unsafe_allow_html=True)
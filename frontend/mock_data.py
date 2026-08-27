import pandas as pd


def get_messages():
    data = [
        {
            "customer_id": "C001",
            "message": "Where is my refund?",
            "intent": "Refund",
            "sentiment": "Negative",
            "language": "English",
            "queue": "Billing",
        },
        {
            "customer_id": "C002",
            "message": "Thank you for solving my issue.",
            "intent": "Technical Support",
            "sentiment": "Positive",
            "language": "English",
            "queue": "Technical Support",
        },
        {
            "customer_id": "C003",
            "message": "Ich kann mich nicht anmelden.",
            "intent": "Account Access",
            "sentiment": "Negative",
            "language": "German",
            "queue": "Account Support",
        },
    ]

    return pd.DataFrame(data)
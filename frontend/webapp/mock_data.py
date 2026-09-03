"""
Placeholder fixture data for the frontend.

Nothing in this file talks to the real classifier. The backend team's
`classify_and_route()` (see ai-ml-backbone/classify.py) and whatever API
wraps it aren't wired up to this app yet, so the dashboard, team queues,
and bulk upload screens render against this static sample data instead.

Once a backend endpoint exists, swap the reads below (in
webapp/blueprints/main.py) for real HTTP calls and delete this file.
"""

MESSAGES = [
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

# Order also drives the "Select Team Queue" dropdown on the team queues screen.
QUEUES = ["Billing", "Technical Support", "Account Support"]

# Ties each queue to one accent used for both its routing tag and its dashboard
# bar, so the same color always means the same queue across the app.
QUEUE_ACCENTS = {
    "Billing": "amber",
    "Technical Support": "teal",
    "Account Support": "plum",
}

"""Routes for the five screens of the Customer Intelligence Classifier."""

import requests
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from ..mock_data import QUEUE_ACCENTS, QUEUES

bp = Blueprint("main", __name__)

CAPABILITIES = [
    {"icon": "🎯", "title": "Intent Classification", "description": "Identifies what the customer actually needs — refund, technical issue, account access, and more."},
    {"icon": "💬", "title": "Sentiment Analysis", "description": "Flags how the customer feels so frustrated messages never sit unnoticed in a queue."},
    {"icon": "🌐", "title": "Language Detection", "description": "Recognizes the language a message was written in before it's routed anywhere."},
    {"icon": "📬", "title": "Smart Routing", "description": "Sends every message straight to the specialist team built to handle it."},
    {"icon": "📁", "title": "Bulk Processing", "description": "Classifies a full CSV of customer messages in a single upload."},
    {"icon": "📊", "title": "Live Analytics", "description": "Tracks volume, sentiment, and queue load on one dashboard."},
]

TEAM_DESCRIPTIONS = {
    "Billing and Payments": "Handles invoicing, payment methods, refunds, and billing disputes.",
    "Customer Service": "General account support and requests that don't fit a specialist queue.",
    "General Inquiry": "Broad, ambiguous questions not yet categorized into a specific team.",
    "Human Resources": "Employee-facing requests: payroll, leave, benefits, onboarding.",
    "IT Support": "Internal tooling, VPN, hardware, and software licensing issues.",
    "Product Support": "Help using product features, bugs, and functionality questions.",
    "Returns and Exchanges": "Product returns, exchanges, and related logistics.",
    "Sales and Pre-Sales": "Pricing questions, demos, and purchase-related inquiries.",
    "Service Outages and Maintenance": "Reports of downtime, outages, and planned maintenance.",
    "Technical Support": "Technical troubleshooting for product or account access issues.",
}

SENTIMENT_MEANINGS = {
    "Positive": "The customer expresses satisfaction, gratitude, or a good experience.",
    "Neutral": "A factual report or question with no strong emotional tone.",
    "Negative": "The customer expresses frustration, complaint, or dissatisfaction.",
}

PRIORITY_MEANINGS = {
    "low": "Routine requests with no urgency.",
    "medium": "Meaningful issues that should be handled promptly.",
    "high": "Urgent or critical issues needing immediate attention.",
}

def api_base():
    return current_app.config["API_BASE_URL"]


@bp.route("/")
def home():
    return render_template("home.html", capabilities=CAPABILITIES)


@bp.route("/bulk-upload", methods=["GET", "POST"])
def bulk_upload():
    if request.method == "POST":
        uploaded = request.files.get("csv_file")
        if not uploaded or uploaded.filename == "":
            flash("Choose a CSV file before uploading.", "error")
        elif not uploaded.filename.lower().endswith(".csv"):
            flash(f'"{uploaded.filename}" is not a CSV file. Choose a .csv file and try again.', "error")
        else:
            safe_name = secure_filename(uploaded.filename)
            try:
                files = {"file": (safe_name, uploaded.stream, "text/csv")}
                resp = requests.post(f"{api_base()}/ingest/batch-upload", files=files, timeout=60)
                resp.raise_for_status()
                result = resp.json()
                flash(
                    f'"{safe_name}" processed: {result["processed"]} classified, {result["failed"]} failed.',
                    "success",
                )
            except requests.RequestException as e:
                flash(f"Could not reach the classification service: {e}", "error")
        return redirect(url_for("main.bulk_upload"))

    return render_template("bulk_upload.html")


@bp.route("/classify", methods=["GET", "POST"])
def classify():
    message_text = ""
    result = None
    if request.method == "POST":
        message_text = request.form.get("message", "").strip()
        if not message_text:
            flash("Enter a customer message before classifying.", "error")
        else:
            try:
                resp = requests.post(
                    f"{api_base()}/ingest",
                    json={"subject": None, "body": message_text, "source": "csv", "language": None},
                    timeout=15,
                )
                resp.raise_for_status()
                result = resp.json()
                flash("Message classified successfully.", "success")
            except requests.RequestException as e:
                flash(f"Could not reach the classification service: {e}", "error")

    return render_template("classify.html", message_text=message_text, result=result)

@bp.route("/dashboard")
def dashboard():
    days = request.args.get("days", type=int)  # None if not provided

    try:
        params = {"days": days} if days else {}
        analytics = requests.get(f"{api_base()}/tickets/analytics", params=params, timeout=15).json()
        recent = requests.get(f"{api_base()}/tickets", params={"limit": 10}, timeout=15).json()
    except requests.RequestException as e:
        flash(f"Could not reach the classification service: {e}", "error")
        analytics = {"total_tickets": 0, "by_queue": {}, "by_sentiment": {}, "by_priority": {}, "by_source": {}}
        recent = {"total": 0, "tickets": []}

    team_counts = {queue: analytics["by_queue"].get(queue, 0) for queue in QUEUES}
    max_count = max(team_counts.values()) if team_counts else 0

    sentiment_counts = {
        "Positive": analytics["by_sentiment"].get("Positive", 0),
        "Neutral": analytics["by_sentiment"].get("Neutral", 0),
        "Negative": analytics["by_sentiment"].get("Negative", 0),
    }

    priority_counts = {
        "low": analytics["by_priority"].get("low", 0),
        "medium": analytics["by_priority"].get("medium", 0),
        "high": analytics["by_priority"].get("high", 0),
    }

    return render_template(
        "dashboard.html",
        messages=recent["tickets"],
        total=analytics["total_tickets"],
        num_teams=len(QUEUES),
        priority_counts=priority_counts,
        team_counts=team_counts,
        max_count=max_count,
        sentiment_counts=sentiment_counts,
        team_accents=QUEUE_ACCENTS,
        selected_days=days, 
    )


@bp.route("/team-queues")
def team_queues():
    selected = request.args.get("queue", QUEUES[0])
    if selected not in QUEUES:
        selected = QUEUES[0]

    try:
        resp = requests.get(f"{api_base()}/tickets", params={"queue": selected, "limit": 50}, timeout=15)
        resp.raise_for_status()
        filtered = resp.json()["tickets"]
    except requests.RequestException as e:
        flash(f"Could not reach the classification service: {e}", "error")
        filtered = []

    return render_template(
        "team_queues.html",
        teams=QUEUES,
        selected=selected,
        messages=filtered,
        team_accents=QUEUE_ACCENTS,
    )


@bp.route("/team-queues/reassign/<ticket_id>", methods=["POST"])
def reassign_ticket(ticket_id):
    new_queue = request.form.get("new_queue")
    if new_queue not in QUEUES:
        flash("Invalid team selected.", "error")
        return redirect(url_for("main.team_queues"))

    try:
        # Uses the PATCH /tickets/{id} endpoint - extend it to accept
        # predicted_queue if it doesn't already (currently only accepts status)
        resp = requests.patch(
            f"{api_base()}/tickets/{ticket_id}",
            json={"predicted_queue": new_queue},
            timeout=15,
        )
        resp.raise_for_status()
        flash("Message reassigned.", "success")
    except requests.RequestException as e:
        flash(f"Could not reassign: {e}", "error")

    return redirect(url_for("main.team_queues", queue=new_queue))

@bp.route("/glossary")
def glossary():
    return render_template(
        "glossary.html",
        team_descriptions=TEAM_DESCRIPTIONS,
        sentiment_meanings=SENTIMENT_MEANINGS,
        priority_meanings=PRIORITY_MEANINGS,
    )
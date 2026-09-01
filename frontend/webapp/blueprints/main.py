"""Routes for the five screens of the Customer Intelligence Classifier."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from ..mock_data import MESSAGES, QUEUE_ACCENTS, QUEUES

bp = Blueprint("main", __name__)

CAPABILITIES = [
    {
        "icon": "🎯",
        "title": "Intent Classification",
        "description": "Identifies what the customer actually needs — refund, technical issue, account access, and more.",
    },
    {
        "icon": "💬",
        "title": "Sentiment Analysis",
        "description": "Flags how the customer feels so frustrated messages never sit unnoticed in a queue.",
    },
    {
        "icon": "🌐",
        "title": "Language Detection",
        "description": "Recognizes the language a message was written in before it's routed anywhere.",
    },
    {
        "icon": "📬",
        "title": "Smart Routing",
        "description": "Sends every message straight to the specialist team built to handle it.",
    },
    {
        "icon": "📁",
        "title": "Bulk Processing",
        "description": "Classifies a full CSV of customer messages in a single upload.",
    },
    {
        "icon": "📊",
        "title": "Live Analytics",
        "description": "Tracks volume, sentiment, and queue load on one dashboard.",
    },
]


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
            # Batch classification isn't connected yet — this only confirms
            # receipt. Hand `uploaded` to the backend's batch endpoint (see
            # classify_and_route() in ai-ml-backbone/classify.py) here once
            # that service exists.
            safe_name = secure_filename(uploaded.filename)
            flash(f'"{safe_name}" received. Batch classification is not connected yet in this build.', "success")
        return redirect(url_for("main.bulk_upload"))

    return render_template("bulk_upload.html")


@bp.route("/classify", methods=["GET", "POST"])
def classify():
    message_text = ""
    if request.method == "POST":
        message_text = request.form.get("message", "").strip()
        if not message_text:
            flash("Enter a customer message before classifying.", "error")
        else:
            # TODO: call classify_and_route() once the backend API exists.
            # For now the form just round-trips the message.
            flash("Message received. The classification backend is not connected yet in this build.", "info")

    return render_template("classify.html", message_text=message_text)


@bp.route("/dashboard")
def dashboard():
    total = len(MESSAGES)
    positive = sum(1 for m in MESSAGES if m["sentiment"] == "Positive")
    negative = sum(1 for m in MESSAGES if m["sentiment"] == "Negative")

    queue_counts = {queue: 0 for queue in QUEUES}
    for m in MESSAGES:
        queue_counts[m["queue"]] = queue_counts.get(m["queue"], 0) + 1
    max_count = max(queue_counts.values()) if queue_counts else 0

    return render_template(
        "dashboard.html",
        messages=MESSAGES,
        total=total,
        positive=positive,
        negative=negative,
        queue_counts=queue_counts,
        max_count=max_count,
        queue_accents=QUEUE_ACCENTS,
    )


@bp.route("/team-queues")
def team_queues():
    selected = request.args.get("queue", QUEUES[0])
    if selected not in QUEUES:
        selected = QUEUES[0]

    filtered = [m for m in MESSAGES if m["queue"] == selected]

    return render_template(
        "team_queues.html",
        queues=QUEUES,
        selected=selected,
        messages=filtered,
        queue_accents=QUEUE_ACCENTS,
    )

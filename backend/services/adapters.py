"""Normalise Slack, email, and CSV payloads to a common shape."""

from typing import Any


def from_slack(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Slack event payloads have no subject line - just message text.
    Expects something like: {"text": "...", "channel": "...", "user": "..."}
    """
    return {
        "subject": None,
        "body": payload.get("text", "").strip(),
        "source": "slack",
        "language": None,  # could be detected later; Slack doesn't tell us directly
    }


def from_email(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Email payloads have a real subject line and body.
    Expects something like: {"subject": "...", "body": "...", "from": "..."}
    """
    return {
        "subject": payload.get("subject", "").strip() or None,
        "body": payload.get("body", "").strip(),
        "source": "email",
        "language": None,
    }


def from_csv_row(row: dict[str, Any]) -> dict[str, Any]:
    """
    A single row from an uploaded CSV. Assumes columns roughly named
    'subject' and 'body' - adjust key names if the actual CSV format differs.
    """
    return {
        "subject": (row.get("subject") or "").strip() or None,
        "body": (row.get("body") or "").strip(),
        "source": "csv",
        "language": row.get("language"),  # CSV might optionally include this
    }
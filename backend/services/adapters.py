"""Normalise Slack, email, and CSV payloads to a common shape."""

from typing import Any
from langdetect import detect, LangDetectException


def detect_language(text: str) -> str | None:
    if not text or not text.strip():
        return None
    try:
        return detect(text)  # returns 'en', 'de', etc.
    except LangDetectException:
        return None


def from_slack(payload: dict) -> dict:
    event = payload.get("event", payload)
    body = event.get("text", "").strip()
    return {
        "subject": None,
        "body": body,
        "source": "slack",
        "language": detect_language(body),
        "source_ref": {"user": event.get("user")},
    }


def from_email(payload: dict) -> dict:
    subject = payload.get("subject", "").strip() or None
    body = payload.get("body", "").strip()
    return {
        "subject": subject,
        "body": body,
        "source": "email",
        "language": detect_language(body),
        "source_ref": {"from": payload.get("from")},
    }


def from_csv_row(row: dict) -> dict:
    subject = (row.get("subject") or "").strip() or None
    body = (row.get("body") or "").strip()
    return {
        "subject": subject,
        "body": body,
        "source": "csv",
        "language": row.get("language") or detect_language(body),
        "source_ref": {"customer_id": row.get("customer_id")} if row.get("customer_id") else None,
    }
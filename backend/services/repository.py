"""Persistence helpers for tickets and batch jobs."""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models import Ticket




def save_ticket(db: Session, classified: dict, source: str, language: str | None,
                 subject: str | None = None, source_ref: dict | None = None) -> Ticket:
    """
    Takes the output of classify_and_route() plus source metadata,
    saves it as a Ticket row, and returns the saved object.
    """
    ticket = Ticket(
        subject=subject,
        body=classified["text"] if "body" not in classified else classified["body"],
        text=classified["text"],
        source=source,
        language=language,
        predicted_queue=classified["predicted_queue"],
        predicted_sentiment=classified["predicted_sentiment"],
        priority=classified["predicted_priority"],
        routed_team=classified["routed_team"],
        source_ref=source_ref,
        classified_at=datetime.now(timezone.utc),
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_ticket(db: Session, ticket_id: UUID) -> Ticket | None:
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def list_tickets(
    db: Session,
    queue: str | None = None,
    sentiment: str | None = None,
    source: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Ticket]:
    """
    Powers both the overall dashboard (no filters) and per-team queue
    views (queue filter set) from the same function.
    """
    query = db.query(Ticket).filter(Ticket.deleted_at.is_(None))

    if queue:
        query = query.filter(Ticket.predicted_queue == queue)
    if sentiment:
        query = query.filter(Ticket.predicted_sentiment == sentiment)
    if source:
        query = query.filter(Ticket.source == source)

    return (
        query.order_by(Ticket.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_analytics_summary(db: Session, days: int | None = None) -> dict:
    """Aggregate counts for the overall dashboard. If `days` is given,
    only counts tickets from the last N days."""
    base = db.query(Ticket).filter(Ticket.deleted_at.is_(None))

    if days:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        base = base.filter(Ticket.created_at >= since)

    by_queue = base.with_entities(Ticket.predicted_queue, func.count(Ticket.id)).group_by(Ticket.predicted_queue).all()
    by_sentiment = base.with_entities(Ticket.predicted_sentiment, func.count(Ticket.id)).group_by(Ticket.predicted_sentiment).all()
    by_priority = base.with_entities(Ticket.priority, func.count(Ticket.id)).group_by(Ticket.priority).all()
    by_source = base.with_entities(Ticket.source, func.count(Ticket.id)).group_by(Ticket.source).all()

    total = base.count()

    return {
        "total_tickets": total,
        "by_queue": dict(by_queue),
        "by_sentiment": dict(by_sentiment),
        "by_priority": dict(by_priority),
        "by_source": dict(by_source),
    }


def get_volume_over_time(db: Session, days: int = 14) -> list[dict]:
    """Daily ticket counts, for a volume trend chart."""
    from datetime import datetime, timedelta, timezone

    since = datetime.now(timezone.utc) - timedelta(days=days)

    rows = (
        db.query(func.date(Ticket.created_at), func.count(Ticket.id))
        .filter(Ticket.deleted_at.is_(None), Ticket.created_at >= since)
        .group_by(func.date(Ticket.created_at))
        .order_by(func.date(Ticket.created_at))
        .all()
    )

    return [{"date": str(date), "count": count} for date, count in rows]
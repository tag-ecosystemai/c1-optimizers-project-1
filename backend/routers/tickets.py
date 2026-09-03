"""Ticket CRUD: list, retrieve, update, delete, reclassify. Plus analytics."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Ticket
from backend.schemas import (
    AnalyticsSummary,
    TicketListResponse,
    TicketResponse,
    TicketUpdate,
    VolumePoint,
)
from backend.services import classifier, repository

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=TicketListResponse)
def list_tickets(
    queue: str | None = None,
    sentiment: str | None = None,
    source: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Powers both the overall dashboard (no filters) and per-team
    queue views (?queue=Technical Support).
    """
    tickets = repository.list_tickets(
        db, queue=queue, sentiment=sentiment, source=source, limit=limit, offset=offset
    )
    return TicketListResponse(
        total=len(tickets),
        tickets=[TicketResponse.model_validate(t) for t in tickets],
    )


@router.get("/analytics", response_model=AnalyticsSummary)
def get_analytics(db: Session = Depends(get_db)):
    """Aggregate counts for the dashboard's summary cards/charts."""
    return AnalyticsSummary(**repository.get_analytics_summary(db))


@router.get("/analytics/volume", response_model=list[VolumePoint])
def get_volume(days: int = 14, db: Session = Depends(get_db)):
    """Daily volume trend for the dashboard's line chart."""
    return repository.get_volume_over_time(db, days=days)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: UUID, db: Session = Depends(get_db)):
    ticket = repository.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketResponse.model_validate(ticket)


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: UUID, payload: TicketUpdate, db: Session = Depends(get_db)):
    ticket = repository.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if payload.status is not None:
        ticket.status = payload.status

    db.commit()
    db.refresh(ticket)
    return TicketResponse.model_validate(ticket)


@router.delete("/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: UUID, db: Session = Depends(get_db)):
    """Soft delete - sets deleted_at rather than removing the row."""
    ticket = repository.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.deleted_at = datetime.now(timezone.utc)
    db.commit()


@router.post("/{ticket_id}/reclassify", response_model=TicketResponse)
def reclassify_ticket(ticket_id: UUID, db: Session = Depends(get_db)):
    """Re-runs the classifier on an existing ticket's text - useful after a model update."""
    ticket = repository.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    result = classifier.classify(subject=ticket.subject, body=ticket.body, language=ticket.language)

    ticket.predicted_queue = result["predicted_queue"]
    ticket.predicted_sentiment = result["predicted_sentiment"]
    ticket.priority = result["predicted_priority"]
    ticket.routed_team = result["routed_team"]
    ticket.classified_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(ticket)
    return TicketResponse.model_validate(ticket)
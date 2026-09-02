# """POST /ingest, /ingest/slack, /ingest/email, /batch-upload."""


"""
Ticket ingestion endpoints.

Supports:
- POST /ingest
- POST /ingest/slack
- POST /ingest/email
- POST /batch-upload

All ingestion paths normalize incoming data into the common Ticket model,
run the ML classifier, and persist the resulting ticket to PostgreSQL.
"""

from __future__ import annotations

import csv
import hashlib
import io
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Ticket
from backend.services import classifier

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["ingestion"])

class IngestRequest(BaseModel):
    """Generic ticket ingestion payload."""

    subject: str | None = None
    body: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    language: str | None = None
    source_ref: dict[str, Any] | None = None
    dedupe_key: str | None = None


class SlackIngestRequest(BaseModel):
    """
    Normalized Slack message payload.

    This is intentionally provider-shaped enough to support the future
    Slack Events API adapter without coupling the classifier to Slack.
    """

    text: str = Field(..., min_length=1)
    channel_id: str
    user_id: str | None = None
    message_ts: str
    thread_ts: str | None = None
    event_id: str | None = None
    team_id: str | None = None
    language: str | None = None


class EmailIngestRequest(BaseModel):
    """Normalized customer-support email payload."""

    subject: str | None = None
    body: str = Field(..., min_length=1)
    sender: str
    recipient: str | None = None
    message_id: str
    thread_id: str | None = None
    in_reply_to: str | None = None
    references: list[str] = Field(default_factory=list)
    language: str | None = None


class IngestResponse(BaseModel):
    """Response returned after successful ingestion."""

    id: str
    source: str
    predicted_queue: str
    predicted_sentiment: str
    routed_team: str
    priority: str
    status: str
    created_at: datetime


class BatchUploadResponse(BaseModel):
    """Summary returned after CSV ingestion."""

    total_rows: int
    created: int
    duplicates: int
    failed: int
    ticket_ids: list[str] = Field(default_factory=list)




def _make_dedupe_key(source: str, identifier: str) -> str:
    """
    Generate a deterministic database-safe dedupe key.

    Examples:
        slack:event_id
        email:message_id
    """
    raw = f"{source}:{identifier}".strip().lower()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _create_ticket(
    *,
    db: Session,
    subject: str | None,
    body: str,
    source: str,
    language: str | None,
    source_ref: dict[str, Any] | None,
    dedupe_key: str,
) -> Ticket:
    """
    Normalize, classify, and persist a ticket.

    The classifier is deliberately independent of the source channel.
    """

    if not body.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ticket body cannot be empty.",
        )

    if not classifier.is_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Classifier is not ready.",
        )

    # Run the existing ML pipeline.
    result = classifier.classify(
        subject=subject,
        body=body,
        language=language,
    )

    ticket = Ticket(
        subject=subject,
        body=body,
        text=f"{subject}\n{body}" if subject else body,
        source=source,
        language=language,
        predicted_queue=result["predicted_queue"],
        predicted_sentiment=result["predicted_sentiment"],
        routed_team=result["routed_team"],
        priority=result["priority"],
        status="open",
        source_ref=source_ref,
        dedupe_key=dedupe_key,
        created_at=_utc_now(),
        classified_at=_utc_now(),
    )

    db.add(ticket)

    try:
        db.commit()
        db.refresh(ticket)
    except IntegrityError:
        db.rollback()

        existing = (
            db.query(Ticket)
            .filter(Ticket.dedupe_key == dedupe_key)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "Ticket has already been ingested.",
                    "ticket_id": str(existing.id),
                },
            )

        logger.exception("Failed to persist ticket.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save ticket.",
        )

    return ticket


def _ticket_response(ticket: Ticket) -> IngestResponse:
    return IngestResponse(
        id=str(ticket.id),
        source=ticket.source,
        predicted_queue=ticket.predicted_queue,
        predicted_sentiment=ticket.predicted_sentiment,
        routed_team=ticket.routed_team,
        priority=ticket.priority,
        status=ticket.status,
        created_at=ticket.created_at,
    )



@router.post(
    "",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_ticket(
    payload: IngestRequest,
    db: Session = Depends(get_db),
) -> IngestResponse:
    """
    Generic ingestion endpoint.

    Useful for:
    - internal systems
    - testing
    - future integrations
    """

    dedupe_key = payload.dedupe_key

    if not dedupe_key:
        # Generic messages without a provider ID still receive a
        # deterministic key based on their content.
        content = (
            f"{payload.source}|"
            f"{payload.subject or ''}|"
            f"{payload.body}"
        )
        dedupe_key = _make_dedupe_key(payload.source, content)

    ticket = _create_ticket(
        db=db,
        subject=payload.subject,
        body=payload.body,
        source=payload.source,
        language=payload.language,
        source_ref=payload.source_ref,
        dedupe_key=dedupe_key,
    )

    return _ticket_response(ticket)



@router.post(
    "/slack",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_slack(
    payload: SlackIngestRequest,
    db: Session = Depends(get_db),
) -> IngestResponse:
    """
    Ingest a normalized Slack message.

    The future Slack Events API adapter should translate Slack's event
    payload into this schema before it reaches this function.
    """

    identifier = payload.event_id or (
        f"{payload.channel_id}:{payload.message_ts}"
    )

    dedupe_key = _make_dedupe_key("slack", identifier)

    source_ref = {
        "provider": "slack",
        "channel_id": payload.channel_id,
        "user_id": payload.user_id,
        "message_ts": payload.message_ts,
        "thread_ts": payload.thread_ts,
        "event_id": payload.event_id,
        "team_id": payload.team_id,
    }

    ticket = _create_ticket(
        db=db,
        subject=None,
        body=payload.text,
        source="slack",
        language=payload.language,
        source_ref=source_ref,
        dedupe_key=dedupe_key,
    )

    return _ticket_response(ticket)



@router.post(
    "/email",
    response_model=IngestResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_email(
    payload: EmailIngestRequest,
    db: Session = Depends(get_db),
) -> IngestResponse:
    """
    Ingest a customer-support email.

    The future Gmail API / Microsoft Graph adapter should translate the
    provider response into this normalized schema.
    """

    dedupe_key = _make_dedupe_key("email", payload.message_id)

    source_ref = {
        "provider": "email",
        "sender": payload.sender,
        "recipient": payload.recipient,
        "message_id": payload.message_id,
        "thread_id": payload.thread_id,
        "in_reply_to": payload.in_reply_to,
        "references": payload.references,
    }

    ticket = _create_ticket(
        db=db,
        subject=payload.subject,
        body=payload.body,
        source="email",
        language=payload.language,
        source_ref=source_ref,
        dedupe_key=dedupe_key,
    )

    return _ticket_response(ticket)



@router.post(
    "/batch-upload",
    response_model=BatchUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def batch_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> BatchUploadResponse:
    """
    Ingest tickets from a CSV file.

    Required CSV column:
        body

    Optional columns:
        subject
        source
        language
        dedupe_key
    """

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A CSV file is required.",
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported.",
        )

    raw = file.file.read()

    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file must be UTF-8 encoded.",
        )

    reader = csv.DictReader(io.StringIO(text))

    if not reader.fieldnames or "body" not in reader.fieldnames:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV must contain a 'body' column.",
        )

    total_rows = 0
    created = 0
    duplicates = 0
    failed = 0
    ticket_ids: list[str] = []

    for row_number, row in enumerate(reader, start=2):
        total_rows += 1

        try:
            body = (row.get("body") or "").strip()

            if not body:
                failed += 1
                logger.warning(
                    "Skipping CSV row %s: empty body.",
                    row_number,
                )
                continue

            subject = (row.get("subject") or "").strip() or None
            source = (row.get("source") or "csv").strip().lower()
            language = (row.get("language") or "").strip() or None

            provided_dedupe = (row.get("dedupe_key") or "").strip()

            if provided_dedupe:
                dedupe_key = provided_dedupe
            else:
                dedupe_key = _make_dedupe_key(
                    "csv",
                    f"{file.filename}:{row_number}:{subject or ''}:{body}",
                )

            # Check before running the classifier so duplicate rows don't
            # consume model work unnecessarily.
            existing = (
                db.query(Ticket)
                .filter(Ticket.dedupe_key == dedupe_key)
                .first()
            )

            if existing:
                duplicates += 1
                continue

            ticket = _create_ticket(
                db=db,
                subject=subject,
                body=body,
                source=source,
                language=language,
                source_ref={
                    "provider": "csv",
                    "filename": file.filename,
                    "row": row_number,
                },
                dedupe_key=dedupe_key,
            )

            created += 1
            ticket_ids.append(str(ticket.id))

        except HTTPException as exc:
            if exc.status_code == status.HTTP_409_CONFLICT:
                duplicates += 1
            else:
                failed += 1

            logger.warning(
                "CSV row %s failed: %s",
                row_number,
                exc.detail,
            )

        except Exception:
            failed += 1
            db.rollback()

            logger.exception(
                "Unexpected error processing CSV row %s.",
                row_number,
            )

    return BatchUploadResponse(
        total_rows=total_rows,
        created=created,
        duplicates=duplicates,
        failed=failed,
        ticket_ids=ticket_ids,
    )

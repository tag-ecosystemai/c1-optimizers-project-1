"""POST /ingest, /ingest/slack, /ingest/email, /batch-upload."""

import csv
import io

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import TicketIngest, TicketResponse
from backend.services import adapters, classifier, repository

router = APIRouter(prefix="/ingest", tags=["ingest"])


def _classify_and_save(db: Session, normalized: dict) -> TicketResponse:
    classified = classifier.classify(
        subject=normalized["subject"],
        body=normalized["body"],
        language=normalized["language"],
    )
    ticket = repository.save_ticket(
        db,
        classified=classified,
        source=normalized["source"],
        language=normalized["language"],
        subject=normalized["subject"],
        source_ref=normalized.get("source_ref"),
    )
    return TicketResponse.model_validate(ticket)


@router.post("", response_model=TicketResponse)
def ingest(payload: TicketIngest, db: Session = Depends(get_db)):
    """Generic entry point - expects already-normalized input."""
    normalized = {
        "subject": payload.subject,
        "body": payload.body,
        "source": payload.source,
        "language": payload.language,
    }
    return _classify_and_save(db, normalized)


@router.post("/slack", response_model=TicketResponse | dict)
def ingest_slack(payload: dict, db: Session = Depends(get_db)):
    if payload.get("type") == "url_verification":
        return {"challenge": payload["challenge"]}

    normalized = adapters.from_slack(payload)
    if not normalized["body"]:
        return {"status": "ignored"}  # skip non-message events (joins, reactions, etc.)

    return _classify_and_save(db, normalized)


@router.post("/email", response_model=TicketResponse)
def ingest_email(payload: dict, db: Session = Depends(get_db)):
    """Raw email payload - normalized via adapters.py first."""
    normalized = adapters.from_email(payload)
    return _classify_and_save(db, normalized)


@router.post("/batch-upload")
def batch_upload(file: UploadFile, db: Session = Depends(get_db)):
    """
    CSV upload - loops over rows, reusing the exact same classify-and-save
    path as a single /ingest call. Batch is a thin wrapper, not a separate system.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    contents = file.file.read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(contents))

    results = []
    errors = []

    for i, row in enumerate(reader):
        try:
            normalized = adapters.from_csv_row(row)
            ticket_response = _classify_and_save(db, normalized)
            results.append(ticket_response)
        except Exception as e:
            errors.append({"row": i, "error": str(e)})

    return {
        "processed": len(results),
        "failed": len(errors),
        "errors": errors,
    }
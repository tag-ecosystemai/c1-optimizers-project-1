"""SQLAlchemy ORM models: Ticket, BatchJob."""

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base

INTENT_QUEUES = (
    "Billing and Payments",
    "Customer Service",
    "General Inquiry",
    "Human Resources",
    "IT Support",
    "Product Support",
    "Returns and Exchanges",
    "Sales and Pre-Sales",
    "Service Outages and Maintenance",
    "Technical Support",
)

SENTIMENTS = ("Negative", "Neutral", "Positive")
SOURCES = ("slack", "email", "csv")
PRIORITIES = ("normal", "urgent")
TICKET_STATUSES = ("open", "in_progress", "resolved")
BATCH_STATUSES = ("pending", "processing", "completed", "failed")


def _in_list(column: str, values: tuple[str, ...]) -> str:
    rendered = ", ".join(f"'{v}'" for v in values)
    return f"{column} IN ({rendered})"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    source: Mapped[str] = mapped_column(String(16), nullable=False)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)

    predicted_queue: Mapped[str] = mapped_column(String(64), nullable=False)
    predicted_sentiment: Mapped[str] = mapped_column(String(16), nullable=False)
    routed_team: Mapped[str] = mapped_column(String(64), nullable=False)

    priority: Mapped[str] = mapped_column(String(16), nullable=False, default="normal")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="open")

    source_ref: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    dedupe_key: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    classified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Labels are CHECK-constrained rather than PG ENUMs so retraining the
    # models does not require a migration.
    __table_args__ = (
        CheckConstraint(_in_list("source", SOURCES), name="ck_tickets_source"),
        CheckConstraint(
            _in_list("predicted_sentiment", SENTIMENTS), name="ck_tickets_sentiment"
        ),
        CheckConstraint(_in_list("priority", PRIORITIES), name="ck_tickets_priority"),
        CheckConstraint(_in_list("status", TICKET_STATUSES), name="ck_tickets_status"),
        Index("ix_tickets_predicted_queue", "predicted_queue"),
        Index("ix_tickets_predicted_sentiment", "predicted_sentiment"),
        Index("ix_tickets_status", "status"),
        Index("ix_tickets_created_at", created_at.desc()),
        Index("ix_tickets_queue_status", "predicted_queue", "status"),
    )

    def __repr__(self) -> str:
        return f"<Ticket {self.id} {self.predicted_queue!r} {self.status!r}>"


class BatchJob(Base):
    __tablename__ = "batch_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    filename: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")

    total_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    error_log: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        CheckConstraint(_in_list("status", BATCH_STATUSES), name="ck_batch_jobs_status"),
        Index("ix_batch_jobs_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<BatchJob {self.id} {self.filename!r} {self.status!r}>"

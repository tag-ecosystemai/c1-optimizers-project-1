"""Pydantic request and response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class ReadinessResponse(BaseModel):
    status: str
    database: bool
    models: bool


class TicketIngest(BaseModel):
    """Input shape for POST /ingest - a normalized message, ready to classify."""
    subject: str | None = None
    body: str
    source: str  # "slack", "email", or "csv"
    language: str | None = None


class TicketResponse(BaseModel):
    """Output shape when returning a classified ticket."""
    id: UUID
    subject: str | None
    body: str
    text: str
    source: str
    language: str | None
    source_ref: dict | None = None

    predicted_queue: str
    predicted_sentiment: str
    priority: str          
    routed_team: str

    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class TicketListResponse(BaseModel):
    total: int
    tickets: list[TicketResponse]


class TicketUpdate(BaseModel):
    status: str | None = None


class AnalyticsSummary(BaseModel):
    total_tickets: int
    by_queue: dict[str, int]
    by_sentiment: dict[str, int]
    by_priority: dict[str, int]
    by_source: dict[str, int]


class VolumePoint(BaseModel):
    date: str
    count: int

class TicketUpdate(BaseModel):
    status: str | None = None
    predicted_queue: str | None = None

class TicketUpdate(BaseModel):
    status: str | None = None
    predicted_queue: str | None = None
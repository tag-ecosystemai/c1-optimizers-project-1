"""Liveness and readiness probes."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import HealthResponse, ReadinessResponse
from backend.services import classifier

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def liveness() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/health/ready", response_model=ReadinessResponse)
def readiness(db: Session = Depends(get_db)) -> JSONResponse:
    database_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        database_ok = False

    models_ok = classifier.is_ready()
    ready = database_ok and models_ok

    body = ReadinessResponse(
        status="ready" if ready else "not_ready",
        database=database_ok,
        models=models_ok,
    )

    code = status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=code, content=body.model_dump())

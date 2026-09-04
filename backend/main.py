"""FastAPI application entrypoint. Builds the app, mounts routers, and
warms the classifier via lifespan before traffic is served."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.config import settings
from backend.routers import health, ingest, tickets
from backend.services import classifier
from scripts.poll_email import check_inbox  # import your existing function

logger = logging.getLogger(__name__)


async def email_polling_loop():
    while True:
        try:
            check_inbox()
        except Exception as e:
            logger.error(f"Email poll failed: {e}")
        await asyncio.sleep(30)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Loading classifier models...")
    classifier.load()
    logger.info("Classifier ready.")

    task = asyncio.create_task(email_polling_loop())

    yield

    task.cancel()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.include_router(health.router)
    app.include_router(ingest.router)
    app.include_router(tickets.router)
    return app


app = create_app()
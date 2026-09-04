"""FastAPI application entrypoint. Builds the app, mounts routers, and
warms the classifier in the background so the port opens immediately."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.config import settings
from backend.routers import health, ingest, tickets
from backend.services import classifier

logger = logging.getLogger(__name__)


async def load_models_background():
    """Runs model loading in a thread so it doesn't block the event loop
    or delay port binding."""
    try:
        await asyncio.to_thread(classifier.load)
        logger.info("Classifier ready.")
    except Exception as e:
        logger.error(f"Classifier failed to load: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting up - port will open immediately, models load in background...")
    asyncio.create_task(load_models_background())
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.include_router(health.router)
    app.include_router(ingest.router)
    app.include_router(tickets.router)
    return app


app = create_app()
import asyncio
import logging
import threading
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.config import settings
from backend.routers import health, ingest, tickets
from backend.services import classifier

logger = logging.getLogger(__name__)


async def load_models_background():
    try:
        await asyncio.to_thread(classifier.load)
        logger.info("Classifier ready.")
    except Exception as e:
        logger.error(f"Classifier failed to load: {e}")


def start_email_poller():
    try:
        import sys
        import time
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
        from scripts.poll_email import check_inbox
        logger.info("Email poller started.")
        while True:
            try:
                check_inbox()
            except Exception as e:
                logger.error(f"Email poll error: {e}")
            time.sleep(30)
    except Exception as e:
        logger.error(f"Email poller failed to start: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting up...")
    asyncio.create_task(load_models_background())
    email_thread = threading.Thread(target=start_email_poller, daemon=True)
    email_thread.start()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.include_router(health.router)
    app.include_router(ingest.router)
    app.include_router(tickets.router)
    return app


app = create_app()
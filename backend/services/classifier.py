import requests
import os
import sys
from pathlib import Path
from typing import Any

ML_SERVICE_URL = os.environ.get("ML_SERVICE_URL")

_loaded = False

def load() -> None:
    global _loaded
    _loaded = True

def is_ready() -> bool:
    return _loaded

def classify(subject: str | None, body: str, language: str | None = None) -> dict[str, Any]:
    response = requests.post(
        f"{ML_SERVICE_URL}/classify",
        json={"subject": subject, "body": body, "language": language},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
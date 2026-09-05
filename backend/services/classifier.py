"""
backend/services/classifier.py

Wraps ai_ml_backbone.classify_and_route.
Models are loaded lazily inside classify.py itself, so calling load()
here is now a no-op — it just imports the module without triggering
any model loading.
"""

import sys
from pathlib import Path
from typing import Any

_ML_DIR = Path(__file__).resolve().parents[2] / "ai-ml-backbone"

_classify_and_route = None


def load() -> None:
    global _classify_and_route

    if _classify_and_route is not None:
        return

    if str(_ML_DIR) not in sys.path:
        sys.path.insert(0, str(_ML_DIR))

    from classify import classify_and_route  # safe now — no models load at import

    _classify_and_route = classify_and_route


def is_ready() -> bool:
    return _classify_and_route is not None


def classify(subject: str | None, body: str, language: str | None = None) -> dict[str, Any]:
    if _classify_and_route is None:
        raise RuntimeError("Classifier not loaded; call load() during startup.")

    return _classify_and_route(subject=subject, body=body, language=language)
"""Wraps ai_ml_backbone.classify_and_route and derives priority."""

import sys
from pathlib import Path
from typing import Any

# ai-ml-backbone is hyphenated, so it cannot be imported as a package yet.
_ML_DIR = Path(__file__).resolve().parents[2] / "ai-ml-backbone"

_classify_and_route = None


def load() -> None:
    """Import the ML module, loading embedder and both SVMs into memory.

    Called once from the app lifespan so the first request does not pay
    the model load.
    """
    global _classify_and_route

    if _classify_and_route is not None:
        return

    if str(_ML_DIR) not in sys.path:
        sys.path.insert(0, str(_ML_DIR))

    from classify import classify_and_route

    _classify_and_route = classify_and_route


def is_ready() -> bool:
    return _classify_and_route is not None


def classify(subject: str | None, body: str, language: str | None = None) -> dict[str, Any]:
    if _classify_and_route is None:
        raise RuntimeError("Classifier not loaded; call load() during startup.")

    result = _classify_and_route(subject=subject, body=body, language=language)
    result["priority"] = derive_priority(result["predicted_sentiment"])
    return result


def derive_priority(sentiment: str) -> str:
    return "urgent" if sentiment == "Negative" else "normal"

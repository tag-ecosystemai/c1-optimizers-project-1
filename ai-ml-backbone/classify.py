"""
classify.py

Core classification logic for the Customer Intelligence Classifier.
Models are loaded lazily on first use to keep startup memory low —
critical for free-tier hosting environments (e.g. Render 512MB).
"""

from sentence_transformers import SentenceTransformer
import joblib
import os
import gc

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')

# Module-level references — None until first call to _ensure_loaded()
_embedder = None
_intent_model = None
_sentiment_model = None
_priority_model = None
_models_loaded = False


def _ensure_loaded():
    global _embedder, _intent_model, _sentiment_model, _priority_model, _models_loaded

    if _models_loaded:
        return

    print("Loading embedding model...")
    _embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    gc.collect()

    print("Loading intent classifier...")
    _intent_model = joblib.load(os.path.join(MODELS_DIR, 'intent_classifier_svm.joblib'))
    gc.collect()

    print("Loading sentiment classifier...")
    _sentiment_model = joblib.load(os.path.join(MODELS_DIR, 'sentiment_classifier_svm.joblib'))
    gc.collect()

    print("Loading priority classifier...")
    _priority_model = joblib.load(os.path.join(MODELS_DIR, 'priority_classifier_svm.joblib'))
    gc.collect()

    _models_loaded = True
    print("All models loaded.")


def build_text(subject: str, body: str) -> str:
    subject = subject or ''
    body = body or ''
    return (subject + ' ' + body).strip()


def classify_and_route(subject: str, body: str, language: str = None) -> dict:
    _ensure_loaded()  # ← loads on first real request, not at import time

    text = build_text(subject, body)
    embedding = _embedder.encode([text])

    predicted_queue = _intent_model.predict(embedding)[0]
    predicted_sentiment = _sentiment_model.predict(embedding)[0]
    predicted_priority = _priority_model.predict(embedding)[0]

    routed_team = predicted_queue

    return {
        "text": text,
        "language": language,
        "predicted_queue": predicted_queue,
        "predicted_sentiment": predicted_sentiment,
        "predicted_priority": predicted_priority,
        "routed_team": routed_team,
    }
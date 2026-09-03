"""
classify.py

Core classification logic for the Customer Intelligence Classifier.
Loads the embedder + all three trained models ONCE, exposes a single
classify_and_route() function used by FastAPI, the CSV batch endpoint,
and the live-traffic simulator alike.
"""

import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from sentence_transformers import SentenceTransformer
import joblib

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')

print("Loading embedding model...")
embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

print("Loading intent classifier...")
intent_model = joblib.load(os.path.join(MODELS_DIR, 'intent_classifier_svm.joblib'))

print("Loading sentiment classifier...")
sentiment_model = joblib.load(os.path.join(MODELS_DIR, 'sentiment_classifier_svm.joblib'))

print("Loading priority classifier...")
priority_model = joblib.load(os.path.join(MODELS_DIR, 'priority_classifier_svm.joblib'))

print("All models loaded.")


def build_text(subject: str, body: str) -> str:
    subject = subject or ''
    body = body or ''
    return (subject + ' ' + body).strip()


def classify_and_route(subject: str, body: str, language: str = None) -> dict:
    """
    Core function: takes a raw message, returns predicted intent (queue),
    sentiment, priority, and a routing decision. Single source of truth -
    /ingest, /batch-upload, and the live simulator all call this.
    """
    text = build_text(subject, body)

    embedding = embedder.encode([text])

    predicted_queue = intent_model.predict(embedding)[0]
    predicted_sentiment = sentiment_model.predict(embedding)[0]
    predicted_priority = priority_model.predict(embedding)[0]

    routed_team = predicted_queue

    result = {
        "text": text,
        "language": language,
        "predicted_queue": predicted_queue,
        "predicted_sentiment": predicted_sentiment,
        "predicted_priority": predicted_priority,
        "routed_team": routed_team,
    }

    return result
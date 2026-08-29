"""
classify.py

Classification logic for the Customer Intelligence Classifier.
Loads the embedder + both trained models once, exposes a single
classify_and_route() function used by FastAPI, the CSV batch endpoint,
and the live-traffic simulator.
"""

from sentence_transformers import SentenceTransformer
import joblib
import os

# --- Load everything once, at import time (not per-request) ---

models_dir = os.path.join(os.path.dirname(__file__), 'models')

print("Loading embedding model...")
embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

print("Loading intent classifier...")
intent_model = joblib.load(os.path.join(models_dir, 'intent_classifier_svm.joblib'))

print("Loading sentiment classifier...")
sentiment_model = joblib.load(os.path.join(models_dir, 'sentiment_classifier_svm.joblib'))

print("All models loaded.")


def build_text(subject: str, body: str) -> str:
    """
    Combine subject + body into a single text field, exactly matching
    the training-time preprocessing. Handles missing subject (e.g. Slack
    messages) the same way the training data did.
    """
    subject = subject or ''
    body = body or ''
    return (subject + ' ' + body).strip()


def classify_and_route(subject: str, body: str, language: str = None) -> dict:
    """
    Core function: takes a raw message (subject + body), returns predicted
    intent (queue), sentiment, and a routing decision.

    This is the SINGLE source of truth for classification logic - both
    /ingest and /batch-upload call this, and so does the live simulator.
    """
    text = build_text(subject, body)

    # Embed once, use for both models
    embedding = embedder.encode([text])

    predicted_queue = intent_model.predict(embedding)[0]
    predicted_sentiment = sentiment_model.predict(embedding)[0]

    # Simple routing logic: queue name IS the team assignment.
    routed_team = predicted_queue

    result = {
        "text": text,
        "language": language,
        "predicted_queue": predicted_queue,
        "predicted_sentiment": predicted_sentiment,
        "routed_team": routed_team,
    }

    return result
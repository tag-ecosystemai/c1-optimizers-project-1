"""
classify.py

Core classification logic for the Customer Intelligence Classifier.
Embeddings are generated via the Hugging Face Inference API (no local
embedding model loaded) to keep memory usage within free-tier limits.
The three SVM classifiers are loaded lazily on first use.
"""

import os
import gc
import time
import joblib
import requests

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')

HF_API_URL = "https://api-inference.huggingface.co/models/paraphrase-multilingual-MiniLM-L12-v2"
HF_TOKEN = os.environ.get("HF_TOKEN")

_intent_model = None
_sentiment_model = None
_priority_model = None
_models_loaded = False


def _ensure_loaded():
    global _intent_model, _sentiment_model, _priority_model, _models_loaded

    if _models_loaded:
        return

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
    print("All classifiers loaded.")


def _get_embedding(text: str) -> list:
    """Calls the HF Inference API to get the embedding for a piece of text.
    Retries once if the model is still warming up on HF's side (503)."""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    for attempt in range(3):
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": text},
            timeout=30,
        )

        if response.status_code == 200:
            return [response.json()]  # wrap in list to match shape SVMs expect

        if response.status_code == 503:
            # HF model is loading on their side — wait and retry
            wait = int(response.headers.get("X-WaitFor", 20))
            print(f"HF model warming up, waiting {wait}s (attempt {attempt + 1}/3)...")
            time.sleep(wait)
            continue

        # Any other error — raise immediately with detail
        raise RuntimeError(
            f"HF Inference API error {response.status_code}: {response.text}"
        )

    raise RuntimeError("HF Inference API did not become ready after 3 attempts.")


def build_text(subject: str, body: str) -> str:
    subject = subject or ''
    body = body or ''
    return (subject + ' ' + body).strip()


def classify_and_route(subject: str, body: str, language: str = None) -> dict:
    _ensure_loaded()

    text = build_text(subject, body)
    embedding = _get_embedding(text)

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
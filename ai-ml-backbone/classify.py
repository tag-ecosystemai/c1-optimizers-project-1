import os
import gc
import joblib

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')

_vectorizer = None
_intent_model = None
_sentiment_model = None
_priority_model = None
_models_loaded = False


def _ensure_loaded():
    global _vectorizer, _intent_model, _sentiment_model, _priority_model, _models_loaded

    if _models_loaded:
        return

    print("Loading TF-IDF vectorizer...")
    _vectorizer = joblib.load(os.path.join(MODELS_DIR, 'tfidf_vectorizer.joblib'))
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
    _ensure_loaded()

    text = build_text(subject, body)
    features = _vectorizer.transform([text])

    predicted_queue = _intent_model.predict(features)[0]
    predicted_sentiment = _sentiment_model.predict(features)[0]
    predicted_priority = _priority_model.predict(features)[0]

    return {
        "text": text,
        "language": language,
        "predicted_queue": predicted_queue,
        "predicted_sentiment": predicted_sentiment,
        "predicted_priority": predicted_priority,
        "routed_team": predicted_queue,
    }
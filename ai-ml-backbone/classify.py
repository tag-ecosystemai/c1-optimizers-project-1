import os
import gc
import numpy as np
import joblib
from tokenizers import Tokenizer
import onnxruntime as ort

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
ONNX_DIR = os.path.join(MODELS_DIR, 'onnx')

_tokenizer = None
_ort_session = None
_intent_model = None
_sentiment_model = None
_priority_model = None
_models_loaded = False


def _ensure_loaded():
    global _tokenizer, _ort_session, _intent_model, _sentiment_model, _priority_model, _models_loaded

    if _models_loaded:
        return

    print("Loading tokenizer from disk...")
    _tokenizer = Tokenizer.from_file(os.path.join(ONNX_DIR, 'tokenizer.json'))
    _tokenizer.enable_padding(pad_id=1, pad_token="<pad>")
    _tokenizer.enable_truncation(max_length=128)
    gc.collect()

    print("Loading ONNX session from disk...")
    _ort_session = ort.InferenceSession(
        os.path.join(ONNX_DIR, 'model_qint8_avx512.onnx'),
        providers=["CPUExecutionProvider"]
    )
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


def _get_embedding(text: str) -> list:
    encoded = _tokenizer.encode(text)
    input_ids = np.array([encoded.ids], dtype=np.int64)
    attention_mask = np.array([encoded.attention_mask], dtype=np.int64)
    token_type_ids = np.zeros_like(input_ids, dtype=np.int64)

    outputs = _ort_session.run(None, {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "token_type_ids": token_type_ids,
    })

    # Mean pooling
    token_embeddings = outputs[0]
    mask = attention_mask[..., np.newaxis].astype(np.float32)
    sum_embeddings = np.sum(token_embeddings * mask, axis=1)
    sum_mask = np.clip(mask.sum(axis=1), a_min=1e-9, a_max=None)
    embedding = sum_embeddings / sum_mask
    return embedding.tolist()


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
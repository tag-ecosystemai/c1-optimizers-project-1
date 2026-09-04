"""scripts/llm_classifier.py — local LLM (Ollama) classification,
for comparison against the trained SVM models. Standalone experiment,
not part of the production classify_and_route() pipeline."""

import requests
import time
import re


def classify_with_llm(text: str, model: str = "llama3.1") -> dict:
    prompt = f"""You are a customer support ticket classifier.

Classify the following support message into:
1. Intent (must be EXACTLY one of these 10 categories):
   Billing and Payments, Customer Service, General Inquiry, Human Resources,
   IT Support, Product Support, Returns and Exchanges, Sales and Pre-Sales,
   Service Outages and Maintenance, Technical Support

2. Sentiment (must be EXACTLY one of): Positive, Neutral, Negative

3. Priority (must be EXACTLY one of): low, medium, high

Message: "{text}"

Respond ONLY in this exact format, nothing else:
Intent: <category>
Sentiment: <sentiment>
Priority: <priority>
"""
    start = time.time()
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False}
    )
    elapsed = time.time() - start
    raw = response.json()["response"]

    intent_match = re.search(r"Intent:\s*(.+)", raw)
    sentiment_match = re.search(r"Sentiment:\s*(\w+)", raw)
    priority_match = re.search(r"Priority:\s*(\w+)", raw)

    return {
        "predicted_queue": intent_match.group(1).strip() if intent_match else None,
        "predicted_sentiment": sentiment_match.group(1).strip() if sentiment_match else None,
        "predicted_priority": priority_match.group(1).strip().lower() if priority_match else None,
        "latency_seconds": elapsed,
        "raw_output": raw,
    }


if __name__ == "__main__":
    test_message = "My latest invoice shows the wrong amount, please help"
    result = classify_with_llm(test_message, model="mistral")
    print(f"Message: {test_message}\n")
    for key, value in result.items():
        print(f"{key}: {value}")
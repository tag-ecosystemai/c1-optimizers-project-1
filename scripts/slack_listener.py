"""scripts/slack_listener.py — Socket Mode listener, forwards messages to /ingest/slack.
No public URL or tunnel needed."""

from dotenv import load_dotenv
load_dotenv()

import os
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
APP_TOKEN = os.environ["SLACK_APP_LEVEL_TOKEN"]   # <- matches your .env
API_URL = "http://127.0.0.1:8000/ingest/slack"

app = App(token=BOT_TOKEN)


@app.event("message")
def handle_message(event, say):
    # Ignore bot's own messages and edits/deletes to avoid loops/noise
    if event.get("subtype") is not None:
        return

    payload = {"event": event}
    resp = requests.post(API_URL, json=payload)
    print(f"Forwarded message -> {resp.status_code}: {event.get('text', '')[:50]}")


if __name__ == "__main__":
    handler = SocketModeHandler(app, APP_TOKEN)
    handler.start()
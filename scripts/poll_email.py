"""scripts/poll_email.py — polls an inbox, forwards new emails to /ingest/email."""

from dotenv import load_dotenv
load_dotenv()

import os
import imaplib
import email
import time
import requests

IMAP_HOST = "imap.gmail.com"
IMAP_USER = os.environ["IMAP_USER"]
IMAP_PASSWORD = os.environ["IMAP_PASSWORD"]
API_URL = "http://127.0.0.1:8000/ingest/email"
POLL_SECONDS = 30


def check_inbox():
    conn = imaplib.IMAP4_SSL(IMAP_HOST)
    conn.login(IMAP_USER, IMAP_PASSWORD)
    conn.select("inbox")

    _, message_ids = conn.search(None, "UNSEEN")
    for msg_id in message_ids[0].split():
        _, data = conn.fetch(msg_id, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])

        subject = msg.get("Subject", "")
        from_addr = msg.get("From", "")
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")

        requests.post(API_URL, json={"subject": subject, "body": body, "from": from_addr})
        print(f"Ingested: {subject}")

    conn.logout()


if __name__ == "__main__":
    print(f"Polling {IMAP_USER} every {POLL_SECONDS}s...")
    while True:
        check_inbox()
        time.sleep(POLL_SECONDS)
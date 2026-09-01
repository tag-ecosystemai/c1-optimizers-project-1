"""Populate the tickets table with realistic sample data.

Usage (from the repo root):

    python scripts/seed_db.py                  # 40 tickets, spread over 14 days
    python scripts/seed_db.py --count 200      # more volume
    python scripts/seed_db.py --reset          # wipe existing rows first
    python scripts/seed_db.py --live           # stream slowly, like real traffic
    python scripts/seed_db.py --dry-run        # classify + print, write nothing

Every ticket is run through the real classifier, so predicted_queue and
predicted_sentiment are genuine model output, not hardcoded labels.
"""

from __future__ import annotations

import argparse
import random
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.database import SessionLocal  # noqa: E402
from backend.models import Ticket  # noqa: E402
from backend.services import classifier  # noqa: E402

# (subject, body) — subject is None for Slack-style messages, which have none.
MESSAGES: list[tuple[str | None, str]] = [
    ("Invoice discrepancy", "My latest invoice shows the wrong amount, please help"),
    ("Double charged", "I was billed twice this month for the same subscription"),
    ("Refund not received", "I was promised a refund three weeks ago and nothing has arrived"),
    ("Update payment method", "How do I change the credit card on file for my account?"),
    ("Question about pricing", "What exactly is included in the enterprise plan?"),
    ("Cancel subscription", "I would like to cancel my plan before the next billing cycle"),
    ("Cannot log in", "I have been locked out of my account since this morning"),
    ("Password reset broken", "The reset link in the email expires before I can use it"),
    ("Account locked", "Too many failed attempts and now I cannot get in at all"),
    ("Two factor issues", "My authenticator app codes are being rejected every time"),
    (None, "the checkout page keeps crashing when I add items to my cart"),
    (None, "Is the API down? Getting 500s across the board for the last hour"),
    (None, "anyone else seeing slow response times on the dashboard?"),
    (None, "the export button does nothing when I click it"),
    ("App crashes on startup", "The mobile app closes immediately after the splash screen"),
    ("Data not syncing", "Changes I make on desktop never appear on my phone"),
    ("Integration failing", "Our webhook stopped receiving events yesterday afternoon"),
    ("Performance degraded", "Reports that used to take seconds now take several minutes"),
    ("Refund request", "I want to return this item, it arrived damaged in the box"),
    ("Wrong item shipped", "I ordered the blue model and received the red one"),
    ("Exchange request", "Can I swap this for a larger size? Never opened the package"),
    ("Return label missing", "The return label was not included with my shipment"),
    ("Order status", "Where is my package? It has been two weeks with no update"),
    ("Delivery delayed", "Tracking has said out for delivery for four days now"),
    ("Payroll question", "When will my payslip for this month be available?"),
    ("Leave request", "How do I submit a request for annual leave?"),
    ("Benefits enrollment", "I missed the enrollment window, can it be reopened?"),
    ("Onboarding paperwork", "Which forms do new hires need to complete first?"),
    ("VPN not connecting", "The company VPN times out on my laptop every morning"),
    ("Laptop replacement", "My machine is four years old and extremely slow now"),
    ("Software license", "I need a license for the design software for my role"),
    ("Printer offline", "The office printer on the second floor is not responding"),
    ("Great service", "Your support team was incredibly helpful yesterday, thank you"),
    ("Very satisfied", "The new dashboard update is exactly what we needed"),
    ("Impressed", "Fastest resolution I have ever had from a support team"),
    ("Thank you", "Whoever fixed our sync issue deserves a raise"),
    ("Demo request", "Can someone walk our team through the enterprise features?"),
    ("Volume discount", "Do you offer reduced rates above 500 seats?"),
    ("Contract renewal", "Our contract expires next month, who handles renewals?"),
    ("Service outage", "Everything has been unreachable for the past twenty minutes"),
    ("Scheduled maintenance", "Was there a planned downtime window this weekend?"),
    ("General question", "Do you have documentation on the reporting API?"),
]

SOURCES = ("email", "slack", "csv")
SOURCE_WEIGHTS = (0.5, 0.3, 0.2)

SLACK_CHANNELS = ("C024BE91L", "C7X2M4KQ9", "C1A5D8N3P")


def make_source_ref(source: str, when: datetime, index: int) -> dict:
    """Build the per-source metadata blob the real adapters will produce."""
    if source == "slack":
        return {
            "channel": random.choice(SLACK_CHANNELS),
            "user": f"U{uuid.uuid4().hex[:8].upper()}",
            "ts": f"{when.timestamp():.6f}",
        }
    if source == "email":
        return {
            "from": f"customer{index % 40}@example.com",
            "message_id": f"<{uuid.uuid4()}@mail.example.com>",
        }
    return {"filename": "support_export.csv", "row": index}


def build_ticket(subject: str | None, body: str, when: datetime, index: int) -> Ticket:
    source = random.choices(SOURCES, weights=SOURCE_WEIGHTS, k=1)[0]

    # Slack has no subject line; drop it so the text matches real Slack traffic.
    if source == "slack":
        subject = None

    result = classifier.classify(subject=subject, body=body, language="en")

    return Ticket(
        subject=subject,
        body=body,
        text=result["text"],
        source=source,
        language="en",
        predicted_queue=result["predicted_queue"],
        predicted_sentiment=result["predicted_sentiment"],
        routed_team=result["routed_team"],
        priority=result["priority"],
        status=random.choices(
            ("open", "in_progress", "resolved"), weights=(0.6, 0.25, 0.15), k=1
        )[0],
        source_ref=make_source_ref(source, when, index),
        dedupe_key=f"seed-{uuid.uuid4()}",
        created_at=when,
        classified_at=when,
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Seed the tickets table with sample data.")
    p.add_argument("--count", type=int, default=40, help="tickets to create (default 40)")
    p.add_argument("--days", type=int, default=14, help="spread over this many days back")
    p.add_argument("--reset", action="store_true", help="delete existing tickets first")
    p.add_argument("--live", action="store_true", help="insert one at a time, with a pause")
    p.add_argument("--delay", type=float, default=1.5, help="seconds between --live inserts")
    p.add_argument("--dry-run", action="store_true", help="classify and print, write nothing")
    p.add_argument("--seed", type=int, help="random seed, for reproducible output")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    print("Loading models (first run downloads ~470MB)...")
    classifier.load()

    db = SessionLocal()
    try:
        if args.reset and not args.dry_run:
            deleted = db.query(Ticket).delete()
            db.commit()
            print(f"Deleted {deleted} existing tickets.")

        now = datetime.now(timezone.utc)
        created = 0

        for i in range(args.count):
            subject, body = MESSAGES[i % len(MESSAGES)]

            if args.live:
                when = datetime.now(timezone.utc)
            else:
                when = now - timedelta(
                    days=random.uniform(0, args.days), hours=random.uniform(0, 24)
                )

            ticket = build_ticket(subject, body, when, i)

            label = subject or body[:40]
            line = (
                f"[{i + 1:>3}/{args.count}] {label[:38]:<38} "
                f"{ticket.predicted_queue:<32} {ticket.predicted_sentiment:<8} "
                f"{ticket.priority}"
            )

            if args.dry_run:
                print(line)
                continue

            db.add(ticket)
            created += 1

            if args.live:
                db.commit()
                print(line, flush=True)
                time.sleep(args.delay)

        if not args.dry_run and not args.live:
            db.commit()

        if args.dry_run:
            print(f"\nDry run: {args.count} classified, nothing written.")
        else:
            total = db.query(Ticket).count()
            print(f"\nInserted {created} tickets. Table now holds {total}.")

    finally:
        db.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

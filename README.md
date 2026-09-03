# TAG AI Engineering Bootcamp: Cohort 1

## Team Optimizers: Project 1

This repository contains Team Optimizers' work for Project 1 of the TAG AI Engineering Bootcamp.

## Team Members

- Hannah Igboke (Project Lead)
- Nunsi Shiaki
- Rachel Onyeamachi Iwebuke
- Salaudeen Sheriffdeen
- Atujuna Emmanuel
- Jayeoba Victor

## Project Brief

To be added when Project 1 begins.

## Objectives

To be completed by the team.

## Tech Stack

To be documented by the team.

## Project Structure

```
c1-optimizers-project-1/
│
├── ai-ml-backbone/
│   ├── classify.py                              — core classify_and_route() function (embed → predict intent + sentiment)
│   ├── eda-and-model-development-notebook.ipynb  — original exploratory/training notebook (gitignored, local only)
│   ├── test.py                                   — standalone script to sanity-check classify.py works
│   ├── requirements.txt                          — Python deps for the ML side (sentence-transformers, sklearn, etc.)
│   └── models/
│       ├── intent_classifier_svm.joblib          — trained SVM, predicts queue (tracked via Git LFS)
│       └── sentiment_classifier_svm.joblib       — trained SVM, predicts sentiment (tracked via Git LFS)
│
├── alembic/                                      — database migration tooling (Alembic)
│   ├── versions/                                 — individual migration files (schema change history)
│   ├── env.py                                    — Alembic's runtime config
│   ├── script.py.mako                            — template used when generating new migrations
│   └── README
│
├── backend/                                      — the FastAPI application
│   ├── __init__.py
│   ├── main.py                                   — app entrypoint; loads classifier on startup; ONLY health router registered so far
│   ├── config.py                                 — settings (DB URL, API host/port, embedding model name) via pydantic-settings
│   ├── database.py                               — SQLAlchemy engine/session setup, get_db() dependency
│   ├── models.py                                 — DB tables: Ticket, BatchJob (SQLAlchemy ORM, not ML models)
│   ├── schemas.py                                — Pydantic schemas; currently only Health/Readiness — ticket/ingest schemas NOT yet written
│   ├── SETUP.md                                  — setup instructions + known issues (well documented)
│   │
│   ├── routers/                                  — API route definitions
│   │   ├── health.py                             — ✅ IMPLEMENTED: /health, /health/ready
│   │   ├── ingest.py                              — ⚠️ STUB ONLY: /ingest, /ingest/slack, /ingest/email, /batch-upload — no code yet
│   │   └── tickets.py                            — ⚠️ STUB ONLY: ticket CRUD — no code yet
│   │
│   ├── services/                                 — business logic layer
│   │   ├── classifier.py                         — ✅ IMPLEMENTED: wraps classify_and_route(), derives priority from sentiment
│   │   ├── adapters.py                           — ⚠️ STUB ONLY: normalize Slack/email/CSV payloads — no code yet
│   │   ├── repository.py                         — ⚠️ STUB ONLY: DB persistence helpers — no code yet
│   │   └── analytics.py                          — ⚠️ STUB ONLY: aggregate endpoints for Streamlit dashboard — no code yet
│   │
│   └── tests/                                    — backend automated tests (contents not yet reviewed)
│
├── docker/
│   └── initdb/
│       └── 01-app-user.sh                        — runs once on fresh DB volume; creates the app's DB role/permissions
│
├── docker-compose.yml                            — spins up Postgres (port 5433 on host, to avoid clashing with local Postgres)
│
├── frontend/                                     — Streamlit app (contents not yet reviewed)
│   └── requirements.txt
│
├── scripts/
│   └── seed_db.py                                — ✅ IMPLEMENTED: populates tickets table using the REAL classifier (not fake data)
│
├── .dockerignore
├── .env.example                                  — template for required environment variables (copy to .env, fill in secrets)
├── .gitignore
├── alembic.ini                                   — Alembic configuration file
└── README.md
```

## Getting Started

Setup instructions will be added by the team.

## Team Workflow

1. Create a branch before working on a feature or task.
2. Do not work directly on the main branch.
3. Push changes to your branch.
4. Open a pull request when the work is ready.
5. Another team member should review the pull request before it is merged.
6. Keep commit messages clear and descriptive.
7. Never commit passwords, API keys, tokens or other secrets.

## Mentor

Assigned mentor: Bash

## Programme

TAG AI Engineering Bootcamp: Cohort 1

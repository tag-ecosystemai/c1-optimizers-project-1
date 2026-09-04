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

NorthStack's support and product teams receive a high volume of messages daily — support tickets, in-app feedback, and reviews — arriving via email, Slack, and CSV exports, in both English and German. Today, a small team of coordinators manually triages every message before it reaches the right specialist team, creating a bottleneck as volume grows.
 
This project builds a system that automatically:
1. Reads an incoming message (from email, Slack, or a bulk CSV upload)
2. Classifies its **intent** (which of 10 teams it belongs to), **sentiment** (Positive / Neutral / Negative), and **priority** (low / medium / high)
3. Routes it to the correct team
4. Surfaces everything through a live dashboard and per-team queue views

Full business context and architecture reasoning: see [`PRD_Customer_Intelligence_Classifier.md`](./PRD_Customer_Intelligence_Classifier.md).

## Objectives

- Diagnose and justify the right ML approach for the problem (classical ML vs. DL vs. LLM vs. RAG vs. agents) rather than defaulting to the most fashionable option
- Train and evaluate real classifiers on a genuine, non-toy dataset, with honest reporting of accuracy, limitations, and failure modes
- Support live ingestion from multiple real channels (Slack, email, CSV) through one shared classification core
- Provide a usable, real-time dashboard for both leadership (overall analytics) and individual teams (their own queue)
- Compare the chosen classical ML approach against local LLMs (zero-shot) on the same task, with real accuracy and latency numbers — not just an assumption

## Tech Stack

| Layer | Technology |
|---|---|
| **ML / Classification** | Python, scikit-learn (SVM), `sentence-transformers` (multilingual embeddings), Hugging Face `transformers` |
| **Backend API** | FastAPI, SQLAlchemy, Alembic (migrations), Pydantic |
| **Database** | PostgreSQL (Docker locally, managed Postgres on Render) |
| **Frontend** | Flask, Jinja2 |
| **Live ingestion** | Slack Bolt SDK (Socket Mode), IMAP (email polling) |
| **LLM comparison** | Ollama (local models — Mistral, Llama 3.1) |
| **Dataset** | [Tobi-Bueck/customer-support-tickets](https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets) (Hugging Face) |
| **Deployment** | Render (Postgres, FastAPI backend, Flask frontend as separate services) |
| **Version control** | Git, Git LFS (for trained model files) |

## Project Structure

```
c1-optimizers-project-1/
│
├── ai-ml-backbone/                # Core ML: embedding + classification logic
│   ├── classify.py                # classify_and_route() — the single source of truth
│   ├── eda-model-development-notebook.ipynb
│   └── models/                    # Trained SVMs (intent, sentiment, priority) — Git LFS
│
├── backend/                       # FastAPI application
│   ├── main.py                    # App entrypoint, router registration, model warmup
│   ├── config.py / database.py / models.py / schemas.py
│   ├── routers/                   # health, ingest, tickets
│   └── services/                  # classifier (ML bridge), adapters, repository, analytics
│
├── frontend/                      # Flask application
│   └── webapp/
│       ├── blueprints/main.py     # All page routes
│       └── templates/             # home, dashboard, team_queues, classify, bulk_upload, glossary
│
├── alembic/                       # Database migrations
├── docker-compose.yml             # Local Postgres
├── scripts/
│   ├── seed_db.py                 # Populate DB with real-classified sample data
│   ├── slack_listener.py          # Live Slack ingestion (Socket Mode)
│   ├── poll_email.py              # Live email ingestion (IMAP polling)
│   └── llm_classifier.py          # Local LLM comparison (Ollama)
│
├── PRD_Customer_Intelligence_Classifier.md
├── requirements.txt
└── README.md
```

## Getting Started

### Requirements
- Python 3.12
- Docker Desktop (running)
- Git LFS
- [Ollama](https://ollama.com) (optional — only needed for the LLM comparison scripts)
### 1. Clone the repo
```bash
git clone https://github.com/tag-ecosystemai/c1-optimizers-project-1.git
cd c1-optimizers-project-1
git lfs pull
```
`git lfs pull` is required — without it, the model files in `ai-ml-backbone/models/` are empty pointer stubs and the app will fail to start.
 
### 2. Set up the environment
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS / Linux
 
pip install -r requirements.txt
```
 
### 3. Configure environment variables
```bash
cp .env.example .env
```
Fill in database credentials and (optionally) Slack/email tokens if testing live ingestion.
 
### 4. Start the database
```bash
docker compose up -d db
python -m alembic upgrade head
```
 
### 5. Run the backend
```bash
uvicorn backend.main:app --reload
```
First run downloads the ~470MB embedding model — this is expected and only happens once. Check `http://localhost:8000/health/ready` and `http://localhost:8000/docs`.
 
### 6. Run the frontend
```bash
python frontend/run.py
```
Visit `http://127.0.0.1:8080`.
 
### 7. (Optional) Seed sample data
```bash
python scripts/seed_db.py --count 40
```
Every seeded message is run through the real trained classifier — not fake/hardcoded labels.
 
### 8. (Optional) Test live ingestion
```bash
python scripts/slack_listener.py    # requires SLACK_BOT_TOKEN, SLACK_APP_LEVEL_TOKEN in .env
python scripts/poll_email.py        # requires IMAP_USER, IMAP_PASSWORD in .env

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

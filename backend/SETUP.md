# Backend Setup

Get the API and database running locally.

## Requirements

- **Python 3.12** — 3.10 will not work, several pinned packages have no cp310 build
- **Docker Desktop** — running
- **Git LFS** — the models are LFS files

## 1. Clone

```bash
git clone https://github.com/tag-ecosystemai/c1-optimizers-project-1.git
cd c1-optimizers-project-1
git checkout backend
git lfs pull
```

`git lfs pull` is not optional. Without it `ai-ml-backbone/models/*.joblib` are 130-byte pointer stubs and the app fails at startup. Check with `ls -lh ai-ml-backbone/models/` — the files should be around 79M and 44M.

## 2. Virtual environment

```bash
python -m venv venv312
venv312\Scripts\Activate.ps1          # Windows PowerShell
source venv312/bin/activate           # macOS / Linux

pip install -r ai-ml-backbone/requirements.txt
```

Confirm the version first — `python --version` must report 3.12.x.

On Windows, if pip fails with `No such file or directory` on a long JupyterLab path, use `ai-ml-backbone/requirements-nojupyter.txt` instead. Same pins minus the notebook UI packages, none of which the backend imports.

## 3. Environment file

```bash
cp .env.example .env
```

Open `.env` and replace both `change-me` values with any password. Use the same value in `POSTGRES_PASSWORD` and in the `DATABASE_URL` — they must match.

`.env` is gitignored. Never commit it.

## 4. Database

```bash
docker compose up -d db
docker compose logs db | tail -5
```

Wait for `database system is ready to accept connections`.

Then create the tables:

```bash
python -m alembic upgrade head
```

Postgres listens on **5433** on the host, not 5432, so it does not collide with a locally installed PostgreSQL.

## 5. Run the API

```bash
uvicorn backend.main:app --reload
```

Run from the **repo root**, not from inside `backend/`.

First start downloads the ~470MB embedding model and appears to hang for a minute. That is normal, and only happens once.

Check it:

- http://localhost:8000/health — `{"status": "ok"}`
- http://localhost:8000/health/ready — `{"status": "ready", "database": true, "models": true}`
- http://localhost:8000/docs — interactive API docs

## 6. Sample data

```bash
python scripts/seed_db.py --dry-run     # classify and print, write nothing
python scripts/seed_db.py               # 40 tickets spread over 14 days
python scripts/seed_db.py --reset       # wipe existing rows first
python scripts/seed_db.py --live        # stream slowly, like real traffic
python scripts/seed_db.py --count 200   # more volume
```

Every message runs through the real classifier, so the predictions are genuine model output.

## Inspecting the database

Command line:

```bash
docker exec -it tag_db psql -U tag_app -d tickets
```

`\dt` lists tables, `\d tickets` shows columns, `\q` quits.

pgAdmin or DBeaver:

```
Host:     localhost
Port:     5433
Database: tickets
User:     tag_app
Password: whatever you set in .env
```

In pgAdmin the tables are under **Databases → tickets → Schemas → public → Tables**.

## Changing the schema

Never create or alter tables by hand. Edit `backend/models.py`, then:

```bash
python -m alembic revision --autogenerate -m "what changed"
python -m alembic upgrade head
```

Read the generated file in `alembic/versions/` before applying it. Autogenerate is good, not perfect.

## Troubleshooting

**`ModuleNotFoundError: No module named 'sentence_transformers'`** — you are on Python 3.10. pip stopped at the first package with no cp310 build and never installed the rest. Rebuild the venv with 3.12.

**`getaddrinfo failed`** — hostname typo, or Docker Desktop is not running.

**`/health/ready` returns 503** — read the body. `database: false` means Postgres is down or `DATABASE_URL` is wrong. `models: false` means the classifier failed to load, usually missing LFS files.

**Tables missing in pgAdmin** — you are probably connected to port 5432 (a local Postgres install) instead of 5433. Run `SELECT version()` — it should report PostgreSQL 16, not 18.

**`ModuleNotFoundError: No module named 'backend'`** — you are running uvicorn from inside `backend/`. Go up to the repo root.

**Edits to `docker/initdb/` do nothing** — those scripts run only on an empty volume. `docker compose down -v` re-runs them, but deletes all data.

## Common commands

```bash
docker compose up -d db        # start the database
docker compose logs -f db      # tail its logs
docker compose down            # stop, keep data
docker compose down -v         # stop, delete all data
python -m alembic current      # which migration is applied
```

## Known issues

**scikit-learn version skew.** The models were pickled with 1.6.1 but `requirements.txt` pins 1.8.0, so loading them logs `InconsistentVersionWarning`. Inference works and predictions are correct, but this should be reconciled with whoever trained the models.

**Intent accuracy.** Sentiment prediction is reliable. Intent skews heavily toward Technical Support — seeding 40 varied messages routes 15 there, including clear Returns and Exchanges and Human Resources cases. Worth reviewing before this reaches users.

Run locally (any laptop)

This project supports two local modes:

1) Quick local dev (no Docker required) — uses SQLite (default)

- Create a virtual environment and install deps:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Run the backend (defaults to `DB_TYPE=sqlite`):

```bash
cd backend
python -m uvicorn app.main:app --reload
# API on http://127.0.0.1:8000
```

2) Optional: run with Postgres (recommended when testing production flows)

- Start Postgres with Docker (example):

```bash
docker run --name smartshiksha-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=smart_shiksha -p 5432:5432 -d postgres:15
```

- Update `backend/.env` or environment variables:

```
DB_TYPE=postgres
POSTGRES_DSN=postgresql+asyncpg://<user>:<password>@127.0.0.1:5432/smart_shiksha
```

- Run migrations (use Alembic) or create minimal tables:

```bash
cd backend
# after configuring alembic, run
alembic upgrade head
# or run the helper script (creates a minimal users table)
python create_pg_tables.py
python -m uvicorn app.main:app --reload
```

Notes
- Default behavior is SQLite so the app works on any laptop without Docker.
- If you prefer Postgres, ensure Docker is running and set `DB_TYPE=postgres`.
- Frontend: `cd frontend && npm install && npm run dev` (requires Node.js).

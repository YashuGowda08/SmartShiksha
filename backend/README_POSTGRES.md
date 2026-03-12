Postgres Integration Notes
=========================

This project supports both MongoDB and Postgres. Use the `DB_TYPE` setting in `app/config.py` to switch between them.

Quick start (Postgres):

1. Install dependencies:

```bash
cd backend
python -m pip install -r requirements.txt
```

2. Start a Postgres instance (Docker):

```bash
docker run --name smartshiksha-postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=smart_shiksha -p 5432:5432 -d postgres:15
```

3. Update `backend/.env` or `app/config.py` to set `DB_TYPE=postgres` and `POSTGRES_DSN` if needed.

4. Run Alembic migrations (recommended):

```bash
cd backend
alembic upgrade head
```

If you prefer quick setup without migrations, ensure tables are created via your ORM models or run a lightweight `create_all` during development (not recommended for production).

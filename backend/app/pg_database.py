"""Async SQL database setup supporting Postgres and SQLite.

This module initializes a working SQLAlchemy async engine. It prefers the
Postgres DSN when `DB_TYPE == 'postgres'` but will automatically fall back to
the local `SQLITE_DSN` if Postgres cannot be reached. The `init_pg_db()`
function performs the runtime check and swaps engines when necessary.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.config import get_settings
import asyncio

settings = get_settings()

# Start with a safe SQLite engine by default so imports never fail.
_dsn = settings.SQLITE_DSN
engine = create_async_engine(_dsn, echo=False, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Track what engine is effectively in use ('sqlite' or 'postgres')
effective_db_type = "sqlite"


async def _try_postgres_and_switch():
    global engine, async_session, effective_db_type
    if settings.DB_TYPE != "postgres":
        return

    # Attempt to create a Postgres engine and perform a quick SELECT 1.
    pg_engine = create_async_engine(settings.POSTGRES_DSN, echo=False, future=True)
    try:
        async with pg_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        # Postgres is reachable — replace the module engine/session
        await engine.dispose()
        engine = pg_engine
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        effective_db_type = "postgres"
    except Exception:
        # Keep SQLite engine as a safe fallback
        await pg_engine.dispose()
        effective_db_type = "sqlite"


async def init_pg_db():
    """Initialize DB engine; try Postgres if configured, else keep SQLite.

    This should be called at application startup.
    """
    try:
        await _try_postgres_and_switch()
    except Exception:
        # Ensure we never raise during startup; fall back to sqlite silently.
        pass


async def close_pg_db():
    await engine.dispose()

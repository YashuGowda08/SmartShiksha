"""Smart Shiksha — FastAPI Application Entry Point (MongoDB)."""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import init_db, close_db
from app.routers import auth, subjects, ai_tutor, exams, mock_tests, progress, admin, textbooks, community

settings = get_settings()

# Ensure uploads directory exists early (before mounting)
os.makedirs("uploads", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup — create MongoDB indexes
    await init_db()
    print("Smart Shiksha API started!")
    print(f"Database type: {settings.DB_TYPE}")
    yield
    # Shutdown — close connection
    await close_db()
    print("Smart Shiksha API shut down")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="AI-Powered Education Platform for Rural India",
    lifespan=lifespan,
)

# CORS
origins = settings.ALLOWED_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(subjects.router, prefix="/api/v1")
app.include_router(ai_tutor.router, prefix="/api/v1")
app.include_router(exams.router, prefix="/api/v1")
app.include_router(mock_tests.router, prefix="/api/v1")
app.include_router(progress.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(textbooks.router, prefix="/api/v1")
app.include_router(community.router, prefix="/api/v1")

# Static files for textbook uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.API_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    # Check DB health depending on configured DB_TYPE
    if settings.DB_TYPE == "mongodb":
        from app.database import client
        try:
            await client.admin.command("ping")
            db_status = "connected"
        except Exception:
            db_status = "disconnected"
    elif settings.DB_TYPE in ("postgres", "sqlite"):
        # SQL check (Postgres or SQLite via SQLAlchemy async engine)
        try:
            from app import pg_database as pgdb
            from sqlalchemy import text
            # Use the effective engine (pgdb.engine) which may be sqlite fallback
            async with pgdb.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            db_status = "connected"
            db_error = None
        except Exception as e:
            db_status = "disconnected"
            db_error = str(e)
    else:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "database": db_status,
        "db_error": db_error if 'db_error' in locals() else None,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

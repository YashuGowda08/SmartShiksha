"""Smart Shiksha — FastAPI Application Entry Point."""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import init_db, close_db
from app.routers import auth, subjects, ai_tutor, exams, mock_tests, progress, admin, textbooks, community, offline

settings = get_settings()

# Ensure uploads directory exists early (before mounting)
os.makedirs("uploads", exist_ok=True)

DB_LABELS = {"sqlite": "SQLite", "postgres": "PostgreSQL", "mongodb": "MongoDB"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    await init_db()
    db_label = DB_LABELS.get(settings.DB_TYPE, settings.DB_TYPE)
    print(f"Smart Shiksha API started!  [{db_label}]")
    yield
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
app.include_router(offline.router, prefix="/api/v1")

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
    return {
        "status": "healthy",
        "database": settings.DB_TYPE,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

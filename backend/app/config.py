"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_PATH = str(BASE_DIR / "smart_shiksha.db")


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Smart Shiksha API"
    DEBUG: bool = False
    API_VERSION: str = "v1"

    # ── Database selector: sqlite | postgres | mongodb ──
    DB_TYPE: str = "sqlite"

    # SQLite (used when DB_TYPE=sqlite)
    SQLITE_PATH: str = DEFAULT_SQLITE_PATH

    # PostgreSQL (used when DB_TYPE=postgres)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "smart_shiksha"

    # MongoDB (used when DB_TYPE=mongodb)
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "smart_shiksha"

    # Legacy — if set, overrides the auto-constructed URL for SQL databases
    DATABASE_URL: Optional[str] = None

    @property
    def database_url(self) -> str:
        """Construct the database URL based on DB_TYPE."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if self.DB_TYPE == "postgres":
            return (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        # Default: sqlite
        return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"

    # Auth
    JWT_SECRET: str = "smart-shiksha-dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 30

    # Groq (cloud AI)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Storage (Supabase or S3)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    S3_BUCKET: str = ""
    AWS_ACCESS_KEY: str = ""
    AWS_SECRET_KEY: str = ""
    AWS_REGION: str = "ap-south-1"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,https://smart-shiksha.vercel.app"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Smart Shiksha API"
    DEBUG: bool = False
    API_VERSION: str = "v1"

    # MongoDB
    MONGODB_URI: str = "mongodb+srv://user:pass@cluster.mongodb.net/?appName=Cluster0"
    MONGODB_DB_NAME: str = "smart_shiksha"
    # Database selection: 'mongodb', 'postgres' or 'sqlite'
    # Default to sqlite for maximum portability on any laptop.
    DB_TYPE: str = "sqlite"
    # Postgres DSN for SQLAlchemy async engine (used when DB_TYPE='postgres')
    POSTGRES_DSN: str = "postgresql+asyncpg://devuser:devpass2@127.0.0.1:5432/smart_shiksha"
    # SQLite DSN for lightweight local development (used when DB_TYPE='sqlite')
    SQLITE_DSN: str = "sqlite+aiosqlite:///./smart_shiksha.db"

    # Clerk
    CLERK_SECRET_KEY: str = ""
    CLERK_PUBLISHABLE_KEY: str = ""

    # Groq
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


@lru_cache()
def get_settings() -> Settings:
    return Settings()

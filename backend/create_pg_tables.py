import asyncio
from app.config import get_settings
from app.pg_database import engine
from sqlalchemy import text

settings = get_settings()

async def create_tables():
    # Create a minimal table to verify connectivity
    async with engine.begin() as conn:
        await conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                clerk_id TEXT,
                email TEXT
            );
            """
        ))
    print("Tables created/verified")

if __name__ == '__main__':
    asyncio.run(create_tables())

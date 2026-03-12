import asyncio
from app.config import get_settings
settings = get_settings()
print('DB_TYPE=', settings.DB_TYPE)
from app.pg_database import engine

async def f():
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            result = await conn.execute(text('SELECT 1'))
            print('OK')
    except Exception as e:
        print('ERR', type(e), e)

asyncio.run(f())

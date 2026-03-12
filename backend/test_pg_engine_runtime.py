import asyncio
from app import pg_database as pgdb
from sqlalchemy import text

async def f():
    print('effective_db_type=', getattr(pgdb,'effective_db_type',None))
    try:
        async with pgdb.engine.connect() as conn:
            r = await conn.execute(text('SELECT 1'))
            print('OK', r.scalar())
    except Exception as e:
        print('ERR', type(e), e)

asyncio.run(f())

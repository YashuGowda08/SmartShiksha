"""Multi-database async connection layer (SQLite / PostgreSQL / MongoDB)."""
from app.config import get_settings

settings = get_settings()

# ── Public API (always available regardless of DB_TYPE) ──
# get_db()   — FastAPI dependency yielding a session / db handle
# init_db()  — create tables / indexes on startup
# close_db() — dispose engine / close client on shutdown

if settings.DB_TYPE == "mongodb":
    # ── MongoDB via Motor + adapter ──
    from motor.motor_asyncio import AsyncIOMotorClient

    _mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    _mongo_database = _mongo_client[settings.MONGODB_DB]

    async def get_db():
        """Yield a MongoSession that is compatible with SQLAlchemy AsyncSession."""
        from app.mongo_adapter import MongoSession
        session = MongoSession(_mongo_database)
        try:
            yield session
        finally:
            pass  # MongoSession has no close; client is long-lived

    async def init_db():
        """Create MongoDB indexes."""
        db = _mongo_database
        await db.users.create_index("clerk_id", unique=True)
        await db.users.create_index("email", unique=True)
        await db.subjects.create_index("board")
        await db.chapters.create_index("subject_id")
        await db.topics.create_index("chapter_id")
        await db.questions.create_index("topic_id")
        await db.mock_tests.create_index("is_active")
        await db.test_questions.create_index("test_id")
        await db.student_attempts.create_index("user_id")
        await db.progress.create_index("user_id")
        await db.chat_sessions.create_index("user_id")
        await db.chat_messages.create_index("session_id")
        await db.textbooks.create_index("subject")
        await db.community_posts.create_index("user_id")
        # Auto-increment counters collection
        await db._counters.create_index("_id")
        print(f"MongoDB: Indexes created in '{settings.MONGODB_DB}'")

    async def close_db():
        _mongo_client.close()
        print("MongoDB: Connection closed")

    # Expose for seed_data compatibility
    engine = None

else:
    # ── SQLite / PostgreSQL via SQLAlchemy async ──
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from app.models import Base

    _connect_args = {}
    if settings.DB_TYPE == "sqlite":
        _connect_args = {"check_same_thread": False}

    engine = create_async_engine(
        settings.database_url,
        echo=settings.DEBUG,
        connect_args=_connect_args,
    )
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def get_db():
        """Dependency that yields an async SQLAlchemy session."""
        async with async_session() as session:
            yield session

    async def init_db():
        """Create all tables."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        db_name = "PostgreSQL" if settings.DB_TYPE == "postgres" else "SQLite"
        print(f"{db_name}: Tables created")

    async def close_db():
        """Dispose the engine."""
        await engine.dispose()

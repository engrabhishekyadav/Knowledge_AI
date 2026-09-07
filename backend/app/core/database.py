import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from app.core.config import settings
from app.models import Base  # Imports all registered models (Note, Task, ChatMessage)

try:
    import asyncpg
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False

logger = logging.getLogger("knowledge_ai.database")
logging.basicConfig(level=logging.INFO)

engine = None
AsyncSessionLocal = None
active_db_type = "unknown"

async def ensure_pg_database_exists(pg_url: str):
    """
    If connected to PostgreSQL, checks if target database exists and auto-creates it if missing.
    """
    if "postgresql" not in pg_url or not HAS_ASYNCPG:
        return
    try:
        raw_url = pg_url.replace("+asyncpg", "")
        parts = raw_url.rsplit("/", 1)
        base_url = parts[0] + "/postgres"
        target_db = parts[1] if len(parts) > 1 else "knowledge_ai"

        conn = await asyncpg.connect(base_url, timeout=3.0)
        dbs = await conn.fetch("SELECT datname FROM pg_database WHERE datname = $1;", target_db)
        if not dbs:
            logger.info(f"Target PostgreSQL database '{target_db}' not found. Auto-creating...")
            await conn.execute(f'CREATE DATABASE "{target_db}";')
            logger.info(f"Database '{target_db}' created successfully.")
        await conn.close()
    except Exception as e:
        logger.debug(f"Auto-database check note: {e}")

async def init_db_engine():
    global engine, AsyncSessionLocal, active_db_type
    if AsyncSessionLocal is not None and engine is not None:
        return AsyncSessionLocal
        
    pg_url = settings.DATABASE_URL
    try:
        if not HAS_ASYNCPG and "asyncpg" in pg_url:
            raise ImportError("asyncpg is not installed in current environment")

        # 1. Ensure database exists
        await ensure_pg_database_exists(pg_url)

        # 2. Connect to primary PostgreSQL
        test_engine = create_async_engine(
            pg_url,
            echo=False,
            future=True,
            connect_args={"timeout": 5} if "asyncpg" in pg_url else {}
        )
        async with test_engine.connect() as conn:
            if "postgresql" in pg_url:
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                    await conn.commit()
                    logger.info("Verified/enabled 'pgvector' extension on PostgreSQL.")
                except Exception as ext_err:
                    logger.warning(f"Note regarding pgvector extension: {ext_err}")
        
        engine = test_engine
        active_db_type = "postgresql_pgvector"
        logger.info("Connected successfully to PostgreSQL database ('knowledge_ai')!")
    except Exception as e:
        logger.warning(f"Primary PostgreSQL connection note ({e}). Activating SQLite async fallback engine...")
        sqlite_url = settings.SQLITE_FALLBACK_URL
        engine = create_async_engine(sqlite_url, echo=False, future=True)
        active_db_type = "sqlite_fallback"
        logger.info(f"SQLite fallback engine initialized at {sqlite_url}")

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )

    # Auto-create all tables in database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Ensure migration columns exist on tables
        if "postgresql" in pg_url and active_db_type != "sqlite_fallback":
            try:
                await conn.execute(text("ALTER TABLE notes ADD COLUMN IF NOT EXISTS user_id VARCHAR(64);"))
                await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notes_user_id ON notes (user_id);"))
            except Exception as e:
                logger.debug(f"notes user_id column note: {e}")

            try:
                await conn.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS user_id VARCHAR(64);"))
                await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tasks_user_id ON tasks (user_id);"))
            except Exception as e:
                logger.debug(f"tasks user_id column note: {e}")

            try:
                await conn.execute(text("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS note_id VARCHAR(64);"))
                await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_chat_messages_note_id ON chat_messages (note_id);"))
            except Exception as e:
                logger.debug(f"chat_messages note_id column note: {e}")
        else:
            # SQLite fallback schema migrations
            try:
                await conn.execute(text("ALTER TABLE notes ADD COLUMN user_id VARCHAR(64);"))
            except Exception:
                pass
            try:
                await conn.execute(text("ALTER TABLE tasks ADD COLUMN user_id VARCHAR(64);"))
            except Exception:
                pass
            try:
                await conn.execute(text("ALTER TABLE chat_messages ADD COLUMN note_id VARCHAR(64);"))
            except Exception:
                pass
        logger.info("Database tables verified/created in database.")

    return AsyncSessionLocal

def async_session_factory() -> AsyncSession:
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        raise RuntimeError("Database engine not initialized")
    return AsyncSessionLocal()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        await init_db_engine()
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


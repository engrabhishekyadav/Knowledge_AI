import os
import asyncio
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
    if not pg_url or "postgresql" not in pg_url:
        raise RuntimeError(
            "FATAL: DATABASE_URL must be a valid PostgreSQL connection string. "
            f"Provided: '{pg_url}'"
        )

    if not HAS_ASYNCPG and "asyncpg" in pg_url:
        raise ImportError(
            "asyncpg is not installed. Please install it using 'pip install asyncpg' "
            "to connect to PostgreSQL."
        )

    # 1. Ensure database exists on the PostgreSQL server
    try:
        await ensure_pg_database_exists(pg_url)
    except Exception as check_err:
        logger.warning(f"Database existence verification notice: {check_err}")

    # 2. Connect to PostgreSQL with pgvector
    try:
        pg_engine = create_async_engine(
            pg_url,
            echo=False,
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=1800,
            connect_args={"timeout": 5} if "asyncpg" in pg_url else {}
        )
        async with pg_engine.connect() as conn:
            # Verify and enable pgvector extension
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                await conn.commit()
                logger.info("Verified/enabled 'pgvector' extension on PostgreSQL.")
            except Exception as ext_err:
                logger.error(f"Failed to enable 'vector' extension on PostgreSQL: {ext_err}")
                raise RuntimeError(
                    f"PostgreSQL pgvector extension error: {ext_err}. "
                    "Ensure your PostgreSQL instance has pgvector installed."
                ) from ext_err

        engine = pg_engine
        active_db_type = "postgresql_pgvector"
        logger.info("Connected successfully to PostgreSQL database with pgvector!")
    except Exception as e:
        error_msg = (
            "\n" + "=" * 70 + "\n"
            "CRITICAL DATABASE CONNECTION FAILURE:\n"
            f"Could not connect to PostgreSQL at: {pg_url}\n"
            f"Exact Error: {e}\n\n"
            "Troubleshooting Steps:\n"
            "1. Start the PostgreSQL container with pgvector using Docker:\n"
            "   docker compose up -d postgres\n"
            "2. Ensure port 5433 (or your configured port) is reachable.\n"
            "3. Verify your DATABASE_URL in backend/.env.\n"
            + "=" * 70 + "\n"
        )
        logger.critical(error_msg)
        raise RuntimeError(error_msg) from e

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )

    # Synchronize database schema via Alembic migrations
    await run_alembic_migrations()

    return AsyncSessionLocal

async def run_alembic_migrations():
    """
    Applies all Alembic migrations up to head programmatically.
    Ensures that database tables, vector indexes, and alembic_version revision history remain synchronized.
    """
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    alembic_ini_path = os.path.join(backend_dir, "alembic.ini")
    if not os.path.exists(alembic_ini_path):
        raise RuntimeError(f"alembic.ini not found at {alembic_ini_path}. Cannot migrate database schema.")

    try:
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config(alembic_ini_path)
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        
        logger.info("Executing Alembic migrations (upgrade head)...")
        await asyncio.to_thread(command.upgrade, alembic_cfg, "head")
        logger.info("Alembic migrations completed successfully.")
    except Exception as mig_err:
        logger.error(f"Alembic programmatic migration failure: {mig_err}")
        raise RuntimeError(f"Database schema migration failed: {mig_err}") from mig_err

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

def get_active_db_type() -> str:
    """Returns the currently active database engine type."""
    global active_db_type
    return active_db_type


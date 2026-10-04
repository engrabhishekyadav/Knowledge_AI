import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
import pgvector.sqlalchemy

from alembic import context

# Ensure backend root is on sys.path
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app.core.config import settings
from app.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set database URL dynamically from app settings if not provided in alembic.ini
db_url = settings.DATABASE_URL
if not db_url or "postgresql" not in db_url:
    raise RuntimeError(
        "Alembic Error: settings.DATABASE_URL must be a valid PostgreSQL connection string. "
        f"Found: '{db_url}'"
    )
config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    # Ensure PostgreSQL vector extension is enabled before running migrations
    if connection.dialect.name == "postgresql":
        try:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        except Exception as ext_err:
            import logging
            logging.getLogger("alembic.env").warning(f"Note on CREATE EXTENSION vector: {ext_err}")

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine for PostgreSQL."""
    try:
        engine = async_engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        async with engine.connect() as conn:
            await conn.run_sync(do_run_migrations)
        await engine.dispose()
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        print("\n" + "=" * 70, file=sys.stderr)
        print("ALEMBIC MIGRATION FAILURE ON POSTGRESQL:", file=sys.stderr)
        print(f"Target Database URL: {db_url}", file=sys.stderr)
        print(f"Failure Reason: {e}", file=sys.stderr)
        print("\nTraceback:\n" + tb_str, file=sys.stderr)
        print("Troubleshooting:", file=sys.stderr)
        print("1. Ensure PostgreSQL is running (e.g. 'docker compose up -d postgres')", file=sys.stderr)
        print("2. Ensure the 'vector' extension is enabled in PostgreSQL", file=sys.stderr)
        print("3. Check backend/.env for valid database credentials", file=sys.stderr)
        print("=" * 70 + "\n", file=sys.stderr)
        raise RuntimeError(f"Alembic migration failed on PostgreSQL: {e}") from e

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

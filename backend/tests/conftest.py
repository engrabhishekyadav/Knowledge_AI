import os
import sys
import pytest
import pytest_asyncio
import httpx
from httpx import ASGITransport

# Ensure backend root is in sys.path
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app.main import app
from app.core.database import init_db_engine

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Initializes the database schema before running tests if PostgreSQL is reachable."""
    try:
        await init_db_engine()
    except RuntimeError as e:
        import logging
        logging.getLogger("tests.database").warning(
            "PostgreSQL is not reachable during test session setup. "
            "Pure algorithm/unit tests will execute; DB-dependent API tests will require PostgreSQL."
        )
    yield

@pytest_asyncio.fixture
async def client():
    """Provides an asynchronous HTTP test client for the FastAPI application."""
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

import os
import asyncio
import asyncpg

# === KROK 1: Tworzymy osobną bazę testową (minibank_test) ===
# Dzięki temu dane z testów NIGDY nie trafią do produkcyjnej bazy "minibank"
async def ensure_test_db():
    conn = await asyncpg.connect(
        host="localhost", port=5433,
        user="bank_admin", password="superhaslo123",
        database="minibank"  # łączymy się z istniejącą bazą, żeby móc stworzyć nową
    )
    exists = await conn.fetchval(
        "SELECT 1 FROM pg_database WHERE datname = 'minibank_test'"
    )
    if not exists:
        await conn.execute("CREATE DATABASE minibank_test")
    await conn.close()

asyncio.run(ensure_test_db())

# === KROK 2: Kierujemy aplikację na bazę testową ===
# MUSI być PRZED importem main/database — bo database.py czyta tę zmienną przy imporcie
os.environ["DATABASE_URL"] = "postgresql+asyncpg://bank_admin:superhaslo123@localhost:5433/minibank_test"

import pytest
from fastapi.testclient import TestClient
from main import app
# from database import Base, engine


@pytest.fixture(scope="session")
def client():
    # TestClient uruchamia lifespan, który tworzy tabele i konto systemowe
    with TestClient(app) as c:
        yield c


# === KROK 3: Czyszczenie danych po KAŻDYM teście ===
# autouse=True → odpala się automatycznie, nie trzeba dodawać do argumentów testu
# Używamy bezpośrednio asyncpg (nie SQLAlchemy engine), żeby uniknąć
# konfliktu event loopów między asyncio.run() a TestClient
@pytest.fixture(autouse=True)
def cleanup_after_test():
    yield  # ← test się wykonuje

    async def cleanup():
        conn = await asyncpg.connect(
            host="localhost", port=5433,
            user="bank_admin", password="superhaslo123",
            database="minibank_test"
        )
        await conn.execute("DELETE FROM transactions")
        await conn.execute("DELETE FROM accounts WHERE id != 0")
        await conn.close()

    asyncio.run(cleanup())

import pytest
import asyncio
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

import main as main_module
from main import app
from database import get_db, Base


# Wymagane dla asynchronicznych testów w pytest
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# 1. Podnosimy kontener PostgreSQL (TYLKO DO TESTÓW)
@pytest.fixture(scope="session")
def db_engine():
    print("\n[TEST SETUP] Uruchamianie Testcontainers (PostgreSQL)...")
    with PostgresContainer("postgres:15-alpine") as postgres:
        # Podmieniamy sterownik na asynchroniczny (asyncpg)
        url = postgres.get_connection_url().replace("psycopg2", "asyncpg")
        # NullPool — każda operacja tworzy nowe połączenie,
        # dzięki czemu nie ma konfliktów między różnymi event loopami
        engine = create_async_engine(url, poolclass=NullPool)

        # Tworzymy schemat bazy wewnątrz kontenera testowego
        async def init_db():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        asyncio.run(init_db())

        yield engine
    print("\n[TEST TEARDOWN] Niszczenie kontenera PostgreSQL...")


# 2. Fabryka sesji testowych (scope=session, bo jest niezmienna)
@pytest.fixture(scope="session")
def test_session_factory(db_engine):
    return async_sessionmaker(db_engine, expire_on_commit=False)


# 3. Wstrzykiwanie zależności (Dependency Override) -> Zastępuje @MockBean
@pytest.fixture(scope="function")
def client(db_engine, test_session_factory):
    # --- Podmieniamy engine i AsyncSessionLocal w module main ---
    # Dzięki temu lifespan() łączy się z testową bazą, a nie produkcyjną (db:5432)
    original_engine = main_module.engine
    original_session_local = main_module.AsyncSessionLocal
    main_module.engine = db_engine
    main_module.AsyncSessionLocal = test_session_factory

    # Podmieniamy oryginalną funkcję 'get_db' z main.py na naszą testową.
    # Każde wywołanie tworzy NOWĄ sesję (brak współdzielenia między event loopami)
    async def override_get_db():
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # TestClient to odpowiednik MockMvc w Springu (nie odpytuje sieci, gada prosto z kodem)
    with TestClient(app) as test_client:
        yield test_client

    # Sprzątamy nadpisanie po teście
    app.dependency_overrides.clear()
    main_module.engine = original_engine
    main_module.AsyncSessionLocal = original_session_local

    # CZYSZCZENIE: Po każdym teście usuwamy wszystkie dane z tabel,
    # żeby testy były od siebie w 100% odizolowane!
    async def cleanup():
        async with test_session_factory() as session:
            for table in reversed(Base.metadata.sorted_tables):
                await session.execute(table.delete())
            await session.commit()

    asyncio.run(cleanup())

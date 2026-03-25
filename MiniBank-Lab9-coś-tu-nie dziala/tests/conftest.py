# MiniBank/tests/conftest.py
# Ten plik ustawia zmienną środowiskową DATABASE_URL na sqlite przed zaimportowaniem modułów aplikacji,
# tworzy schemę raz na sesję i czyści dane po każdym teście.

# Testy będą używały lokalnej bazy SQLite (test_minibank.db), nie dotykały produkcyjnego Postgresa
# Krytyczne: ustawienie os.environ["DATABASE_URL"] odbywa się zanim zaimportujemy:
# - MiniBank.database
# - MiniBank.main
# Dzięki temu moduł database.py utworzy silnik (engine) dla SQLite, a nie dla Postgresa.

# Tworzenie tabel wykonywane jest raz na sesję (fixture prepare_db)
#                          — to przyspiesza testy i daje stabilne środowisko

#$ Po każdym teście czyścimy tabele (zostawiając konto systemowe id=0).
# To zapobiega „wyciekom” danych testowych do bazy, które potem mogłyby wpłynąć na kolejne testy.

# Ten conftest.py jest przeznaczony tylko dla testów (umieść go w MiniBank/tests/).
# Nie ma sensu mieć conftest.py w katalogu pakietu MiniBank (to by wpływało globalnie).

import os
import sys
import asyncio
from pathlib import Path

import pytest
from starlette.testclient import TestClient
from sqlalchemy import text

# 1) Ustal ścieżkę do katalogu projektu (katalog, który zawiera folder MiniBank)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT_STR = str(PROJECT_ROOT)
if PROJECT_ROOT_STR not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_STR)

# 2) Ustaw absolutny DATABASE_URL wskazujący na plik SQLite do testów
DB_FILE = PROJECT_ROOT / "test_minibank.db"
# Używamy pełnej ścieżki (as_posix() działa też na Windows)
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{DB_FILE.as_posix()}"

# 3) Importy aplikacji PO ustawieniu env i sys.path
from MiniBank.database import engine
from MiniBank.main import app
from MiniBank.models import Base

# 4) Funkcje pomocnicze do tworzenia schemy i czyszczenia danych
def _create_tables():
    async def _create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(_create())


def _cleanup_db():
    async def _cleanup():
        async with engine.begin() as conn:
            # Usuń zapisane transakcje i konta testowe (zostaw konto systemowe id=0)
            await conn.execute(text("DELETE FROM transactions"))
            await conn.execute(text("DELETE FROM accounts WHERE id != 0"))
    asyncio.run(_cleanup())


# 5) Fixture tworząca tabele raz per test session
# Tworzenie tabel wykonywane jest raz na sesję (fixture prepare_db)
#                          — to przyspiesza testy i daje stabilne środowisko
@pytest.fixture(scope="session", autouse=True)
def prepare_db():
    _create_tables()
    yield
    # Jeśli chcesz możesz odkomentować drop_all:
    # asyncio.run(lambda: engine.begin().run_sync(Base.metadata.drop_all))


# 6) TestClient (uruchamia lifespan aplikacji)
@pytest.fixture
def client(prepare_db):
    with TestClient(app) as c:
        yield c


# 7) Autouse fixture: czyść dane po każdym teście (zapewnia izolację)
@pytest.fixture(autouse=True)
def cleanup_after_test():
    yield
    _cleanup_db()

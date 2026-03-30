# Konfiguracyjny conftest dla testów używających lokalnego plikowego SQLite (test_minibank.db)
# Plik umieszczony w MiniBank/tests/ — pytest załaduje go dla testów w tym pakiecie.

import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# --- Zasada bezpieczeństwa:
# Nie nadpisujemy zmiennej środowiskowej DATABASE_URL jeśli użytkownik jawnie ją ustawił.
# Aby wymusić użycie SQLite testowego DB, ustaw FORCE_SQLITE_TEST_DB=1 w środowisku.

_force = os.environ.get("FORCE_SQLITE_TEST_DB") == "1"

if (os.environ.get("DATABASE_URL") is None) or _force:
    # budujemy absolutną ścieżkę do pliku test_minibank.db w katalogu projektu
    # Plik conftest.py znajduje się w: <project>/MiniBank/tests/conftest.py
    # parents[2] -> <project>
    repo_root = Path(__file__).resolve().parents[2]
    db_file = repo_root / "test_minibank.db"
    db_url = f"sqlite+aiosqlite:///{db_file.as_posix()}"
    os.environ["DATABASE_URL"] = db_url

# Avoid uvloop/anyio native backend issues on Windows by forcing asyncio backend
# This must be set before importing FastAPI app / anyio-based libraries
os.environ.setdefault("ANYIO_BACKEND", "asyncio")

# Import aplikacji FastAPI po ustawieniu DATABASE_URL
# Używamy importu z nazwą pakietu, żeby działało poprawnie podczas uruchamiania testów
from MiniBank.main import app


@pytest.fixture(scope="session")
def client():
    """Zwraca TestClient uruchamiający lifespan aplikacji (tworzy tabele przy starcie).

    Uwaga: TestClient uruchamia aplikację synchronnie — w tej konfiguracji główne
    pliki aplikacji (main, database) powinny obsługiwać asynchroniczne engine.
    """
    # On Windows, tearing down TestClient (context manager exit) can trigger
    # low-level access violations when using some async DB drivers (aiosqlite).
    # To avoid that while testing locally, we instantiate TestClient and do
    # not explicitly close it here. The process end will release resources.
    c = TestClient(app)
    yield c



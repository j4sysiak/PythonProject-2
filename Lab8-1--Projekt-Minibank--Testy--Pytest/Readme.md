Lab8-1
------

Lab8-1--Projekt-Minibank--Testy--Pytest
---------------------------------------

W świecie Pythona standardem branżowym jest `pytest`. 
Zrobimy teraz `Black-box testing` – czyli testy, które z zewnątrz uderzają w Twój działający kontener Dockera i sprawdzają, 
czy zachowuje się tak, jak zdefiniowaliśmy w kontraktach.

Krok 1: Instalacja
------------------
Otwórz nowy terminal w PyCharmie (na swoim komputerze, upewnij się, że masz aktywne środowisko wirtualne .venv) i zainstaluj:
`pip install pytest requests`

Krok 2: Utworzenie ulotnej bazy danych, żeby testy nie wpływały na dane produkcyjne
-----------------------------------------------------------------------------------
Uruchamianie testów integracyjnych na "żywej", deweloperskiej (lub o zgrozo produkcyjnej!) bazie danych 
to najcięższy grzech początkujących. 
Zostawia śmieci, powoduje konflikty ID i niszczy wiarygodność testów.

W świecie Java / Spring Boot użyłbyś do tego:
  1. `@DataJpaTest`
  2. bazy `H2 (In-Memory)`
  3. biblioteki `Testcontainers`

W `FastAPI` zrobimy dokładnie to samo! 
Użyjemy wbudowanego w `FastAPI` mechanizmu `Dependency Override` (odpowiednik `@MockBean ze Springa`) oraz `Testcontainers`, 
żeby powołać do życia "ulotną" bazę `PostgreSQL` tylko na czas trwania testów.

A. Instalacja narzędzi testowych
-----------------------------
W swoim terminalu (w środowisku wirtualnym) zainstaluj paczki potrzebne do profesjonalnego testowania:
`pip install pytest-asyncio httpx testcontainers`

B. Magiczny plik conftest.py (Setup & Teardown)
-----------------------------------------------
W Pytonie nie używamy klas z `@BeforeAll` i `@AfterEach`. 
Używamy pliku `conftest.py`, który `pytest` wykrywa automatycznie. 
Tu skonfigurujemy `Testcontainers` i nadpiszemy połączenie z bazą.

Utwórz plik `conftest.py` w głównym folderze (MiniBank) i wklej:

```python
import pytest
import asyncio
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

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
        engine = create_async_engine(url)
        
        # Tworzymy schemat bazy wewnątrz kontenera testowego
        async def init_db():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        asyncio.run(init_db())
        
        yield engine
    print("\n[TEST TEARDOWN] Niszczenie kontenera PostgreSQL...")

# 2. Sesja bazy z automatycznym czyszczeniem po KAŻDYM TEŚCIE
@pytest.fixture(scope="function")
async def db_session(db_engine):
    AsyncTestSession = async_sessionmaker(db_engine, expire_on_commit=False)
    async with AsyncTestSession() as session:
        yield session
        # CZYSZCZENIE: Po każdym teście usuwamy wszystkie dane z tabel, 
        # żeby testy były od siebie w 100% odizolowane!
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()

# 3. Wstrzykiwanie zależności (Dependency Override) -> Zastępuje @MockBean
@pytest.fixture(scope="function")
def client(db_session):
    # Podmieniamy oryginalną funkcję 'get_db' z main.py na naszą testową
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    # TestClient to odpowiednik MockMvc w Springu (nie odpytuje sieci, gada prosto z kodem)
    with TestClient(app) as test_client:
        yield test_client
        
    # Sprzątamy nadpisanie po teście
    app.dependency_overrides.clear()
```

C. Utworzenie pliku testowego (test_api.py)
-------------------------------------------
Utwórz test `test_api.py` w głównym folderze (MiniBank) i wklej:
Test będzie używał wygenerowanego wyżej clienta (naszego `MockMvc`).
Dzięki temu testy będą uderzać w prawdziwe endpointy API, ale z izolowaną, ulotną bazą danych,
która jest tworzona i niszczona na czas trwania testów.

```python
import pytest

# Przekazujemy 'client' jako argument - Pytest sam wstrzyknie go z conftest.py!
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200

# Włączamy asynchroniczność dla testów bazodanowych
@pytest.mark.asyncio
async def test_create_account(client):
    payload = {
        "owner_name": "Testowy User",
        "initial_balance": 500.0,
        "currency": "PLN"
    }
    response = client.post("/accounts", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["owner_name"] == "Testowy User"
    assert float(data["balance"]) == 500.0

@pytest.mark.asyncio
async def test_transfer_insufficient_funds(client):
    # Tworzymy konta w TESTOWEJ bazie
    acc1 = client.post("/accounts", json={"owner_name": "Adam", "initial_balance": 50.0, "currency": "PLN"}).json()
    acc2 = client.post("/accounts", json={"owner_name": "Bartek", "initial_balance": 0.0, "currency": "PLN"}).json()
    
    # Próbujemy przelać za dużo
    transfer_payload = {
        "from_account_id": acc1["id"],
        "to_account_id": acc2["id"],
        "amount": 100.0
    }
    
    response = client.post("/convert-transfer", json=transfer_payload)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Brak środków"
```

Co się teraz stanie?
--------------------
Zanim odpalisz testy, zrozum potęgę tej architektury:
Nie musisz mieć odpalonego docker-compose up! (TestClient uruchamia FastAPI bezpośrednio w pamięci RAM).
Testcontainers pobierze i uruchomi w tle miniaturowego Postgresa tylko na czas trwania testów.
Po każdym def test_... baza zostanie "wyczyszczona" do zera.
Gdy testy się skończą, kontener bazy zostanie zniszczony i usunięty z Twojego dysku.

Odpal testy!
------------
Mając cały czas odpalonego Dockera z Twoim API w tle, otwórz terminal i wpisz po prostu:
`pytest test_api.py -v`

(Flaga -v oznacza "verbose", dzięki czemu pytest wypisze nazwy poszczególnych testów na zielono, zamiast pokazywać tylko kropki).

(Przy pierwszym uruchomieniu może to potrwać parę sekund, bo `Testcontainers` musi pobrać obraz `Postgresa` do izolowanego środowiska).
Teraz Twoja deweloperska baza danych (ta z historii w przeglądarce) zostaje całkowicie nienaruszona. 
Testujesz system dokładnie tak, jak to się robi na potokach CI/CD (GitHub Actions / Jenkins).

Daj znać, jak testy przejdą i czy ta architektura trafia w Twoje inżynierskie oczekiwania!


Dlaczego to jest potężne (Inżynieria):
--------------------------------------
Automatyzacja Zaufania: 
Właśnie stworzyłeś zautomatyzowanego QA (testera). 
Kiedy w następnym kroku będziemy dłubać w bebechach bazy danych (Optymistyczne Blokowanie),
wystarczy że wpiszesz `pytest`. 
Jeśli zaświeci się na zielono – możesz iść na kawę. 
Jeśli na czerwono – wiesz, że zepsułeś reguły biznesowe.

Dokumentacja kodu: 
Testy w Pythonie często służą jako "żywa dokumentacja". 
Ktoś nowy przychodzi do projektu, czyta `test_transfer_insufficient_funds` i od razu wie, 
jak API ma się zachować przy braku środków (kod 400).

Odpal te testy. 
Jeśli konsola zaświeci się na zielono (4 passed), masz oficjalnie kod produkcyjny okryty testami integracyjnymi.

Daj znać jak poszło, a wchodzimy prosto w Opcję 2 (Optymistyczne blokowanie i mechanizm wersji), 
żeby pokazać jak rozwiązuje się współbieżność w gigantycznych systemach!


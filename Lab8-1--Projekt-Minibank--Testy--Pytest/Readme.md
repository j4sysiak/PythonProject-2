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
Uruchamianie testów integracyjnych na "żywej", deweloperskiej (lub o zgrozo produkcyjnej!) bazie danych to najcięższy grzech początkujących. 
Zostawia śmieci, powoduje konflikty ID i niszczy wiarygodność testów.

W świecie Java / Spring Boot użyłbyś do tego:
  1. `@DataJpaTest`
lub
  2. bazy `H2 (In-Memory)`
lub
  3. biblioteki `Testcontainers`

W `FastAPI` zrobimy dokładnie to samo! 
Użyjemy wbudowanego w `FastAPI` mechanizmu `Dependency Override` (odpowiednik `@MockBean ze Springa`) oraz `Testcontainers`, 
żeby powołać do życia "ulotną" bazę `PostgreSQL` tylko na czas trwania testów.

A. Instalacja narzędzi testowych
--------------------------------
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

```

C. Utworzenie pliku testowego (test_api.py)
-------------------------------------------
Utwórz test `test_api.py` w głównym folderze (MiniBank):
Ten test będzie używał wygenerowanego wyżej clienta (naszego `MockMvc`) czyli conftest.py
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

(Flaga -v oznacza "verbose", dzięki czemu pytest wypisze nazwy poszczególnych testów na zielono, 
                                                                       zamiast pokazywać tylko kropki).

(Przy pierwszym uruchomieniu może to potrwać parę sekund, bo `Testcontainers` musi pobrać obraz `Postgresa` 
do izolowanego środowiska).
Teraz Twoja deweloperska baza danych (ta z historii w przeglądarce) zostaje całkowicie nienaruszona. 
Testujesz system dokładnie tak, jak to się robi na potokach `CI/CD` (`GitHub Actions / Jenkins`).

Daj znać, jak testy przejdą i czy ta architektura trafia w Twoje inżynierskie oczekiwania!
--> Dziala!!

````
$ pytest test_api.py -v
============================================================================== test session starts ===============================================================================
platform win32 -- Python 3.14.0, pytest-9.0.2, pluggy-1.6.0 -- C:\dev\python-projects\PycharmProjects\PythonProject-2\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\dev\python-projects\PycharmProjects\PythonProject-2\MiniBank
configfile: pytest.ini
plugins: anyio-4.12.1, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collected 3 items                                                                                                                                                                 

test_api.py::test_health_check PASSED                                                                                                                                       [ 33%]Windows fatal exception: access violation

Thread 0x00008484 (most recent call first):
  File "C:\Users\j4sys\AppData\Local\Programs\Python\Python314\Lib\threading.py", line 1132 in join
      [...]
  File "C:\dev\python-projects\PycharmProjects\PythonProject-2\.venv\Scripts\pytest.exe\__main__.py", line 7 in <module>
  File "<frozen runpy>", line 88 in _run_code
  File "<frozen runpy>", line 198 in _run_module_as_main

Current thread's C stack trace (most recent call first):
  <cannot get C stack on this system>

test_api.py::test_create_account PASSED                                                                                                                                     [ 66%]Windows fatal exception: access violation

Thread 0x00008484 (most recent call first):
  File "C:\Users\j4sys\AppData\Local\Programs\Python\Python314\Lib\threading.py", line 1132 in join
    [...]
  File "C:\dev\python-projects\PycharmProjects\PythonProject-2\.venv\Scripts\pytest.exe\__main__.py", line 7 in <module>
  File "<frozen runpy>", line 88 in _run_code
  File "<frozen runpy>", line 198 in _run_module_as_main

Current thread's C stack trace (most recent call first):
  <cannot get C stack on this system>

test_api.py::test_transfer_insufficient_funds PASSED                                                                                                                        [100%]Windows fatal exception: access violation

Thread 0x00008484 (most recent call first):
  File "C:\Users\j4sys\AppData\Local\Programs\Python\Python314\Lib\threading.py", line 1132 in join
      [...]
  File "C:\dev\python-projects\PycharmProjects\PythonProject-2\.venv\Scripts\pytest.exe\__main__.py", line 7 in <module>
  File "<frozen runpy>", line 88 in _run_code
  File "<frozen runpy>", line 198 in _run_module_as_main

Current thread's C stack trace (most recent call first):
  <cannot get C stack on this system>


=============================================================================== 3 passed in 6.72s ====
````


Dlaczego to jest potężne (Inżynieria):
--------------------------------------
Automatyzacja Zaufania: 
Właśnie stworzyłeś zautomatyzowanego QA (testera). 
Kiedy w następnym kroku będziemy dłubać w bebechach bazy danych (Optymistyczne Blokowanie),
wystarczy że wpiszesz `pytest test_api.py -v`  
Jeśli zaświeci się na zielono – możesz iść na kawę. 
Jeśli na czerwono – wiesz, że zepsułeś reguły biznesowe.

Dokumentacja kodu: 
Testy w Pythonie często służą jako "żywa dokumentacja". 
Ktoś nowy przychodzi do projektu, czyta `test_transfer_insufficient_funds` i od razu wie, 
jak API ma się zachować przy braku środków (kod 400).
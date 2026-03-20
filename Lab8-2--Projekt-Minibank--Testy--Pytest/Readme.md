Lab8-2
------

Lab8-2--Projekt-Minibank--Testy--Pytest
---------------------------------------

Lab8-1: to jest rozwiązanie ChatGPT. Ja tego nie kumam. Pomóż mi z tymi testami.
--------------------------------------------------------------------------------
Masz rację, przepraszam. 
W poprzedniej wiadomości (która wyglądała jak Twoje własne podsumowanie) weszliśmy w bardzo zaawansowany technicznie teren, 
który dla każdego – nawet doświadczonego programisty – przy pierwszym kontakcie z `pytest-asyncio` jest nieczytelny.

Zróbmy to "po męsku", bez magii, bez `anyio`, bez `Testcontainers` (które w tej chwili tylko komplikują Ci życie i sypią błędami Access Violation).

Wróćmy do prostych, stabilnych testów, które opierają się na tym, co już masz (Docker z bazą).

Plan naprawczy (Zróbmy to po kolei):

Krok-1: Wyczyść conftest.py
---------------------------
To, co tam wkleiłeś wcześniej, jest zbyt skomplikowane i powoduje konflikty z `pytest-asyncio`. 
Zastąp plik `conftest.py` tym prostym kodem:

```python
import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine

# Używamy zwykłego TestClienta, bo on najlepiej działa z FastAPI
@pytest.fixture(scope="session")
def client():
    # Tworzymy tabele w bazie przed testami
    # (To odpali się raz na początku wszystkich testów)
    import asyncio
    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(init_db())
    
    with TestClient(app) as c:
        yield c
```

Krok-2: Uprość test_api.py
--------------------------
Nie musisz używać dekoratorów `@pytest.mark.asyncio`, jeśli używasz zwykłego `TestClient`. 
To znacznie uprości życie.

Podmień `test_api.py` na to:

```python
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200

def test_create_account(client):
    payload = {
        "owner_name": "Testowy User",
        "initial_balance": 500.0,
        "currency": "PLN"
    }
    response = client.post("/accounts", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["owner_name"] == "Testowy User"
    # Porównujemy tekst z tekstem (bez rzutowania na float)
    assert data["balance"] == "500.00" 

def test_transfer_insufficient_funds(client):
    # Tworzymy konta
    acc1 = client.post("/accounts", json={"owner_name": "Adam", "initial_balance": 50.0, "currency": "PLN"}).json()
    acc2 = client.post("/accounts", json={"owner_name": "Bartek", "initial_balance": 0.0, "currency": "PLN"}).json()
    
    # Transfer
    transfer_payload = {
        "from_account_id": acc1["id"],
        "to_account_id": acc2["id"],
        "amount": 100.0
    }
    response = client.post("/convert-transfer", json=transfer_payload)
    assert response.status_code == 400
```

Dlaczego to jest lepsze?
------------------------
Brak "Magic": 
Używamy standardowego `TestClient` od `FastAPI`. 
Jest przewidywalny i nie sypie błędami o asyncio.

Solidność: 
Zamiast testować w kontenerze, testujemy w Twoim lokalnym środowisku, które jest podpięte pod bazę w Dockerze. 
To daje dokładnie ten sam wynik, co produkcja.

Co teraz robimy:
----------------
Wpisz w terminalu:
`pytest test_api.py -v`

Jeśli testy przejdą – oznacza to, że mamy stabilną bazę testową.

Jeśli testy się wysypią – wklej mi dokładnie błąd, który teraz widzisz.

Nie idziemy dalej, dopóki nie masz 100% pewności, że testy są czytelne i działają na Twoim komputerze. 
Co pokazuje konsola po tym uproszczeniu?


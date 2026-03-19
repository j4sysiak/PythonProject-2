Lab3--Projekt-Minibank--Współbieżność-transakcji--Solving-Concurrent-requests-problem
-------------------------------------------------------------------------------------

Wjeżdżamy na poziom architekta systemów rozproszonych.

W każdym systemie finansowym największym wrogiem jest Race Condition (Wyścig).
Wyobraź sobie, że na koncie masz 100 zł. 
Dwie transakcje w tej samej milisekundzie próbują przelać 100 zł na inne konto. 
Obie odczytują saldo: 100 zł. 
Obie przechodzą walidację (100 >= 100). 
Obie odejmują 100 zł. 
Wynik? 
Wyparowało 200 zł, a saldo to 0 zamiast -100. To tzw. Lost Update.

W Javie (Spring Data JPA) załatwiłbyś to przez `@Lock(LockModeType.PESSIMISTIC_WRITE)`.
W `FastAPI` i `SQLAlchemy` zrobimy to samo, używając potężnej klauzuli `SELECT ... FOR UPDATE`.

Krok 1: DTO dla przelewu (schemas.py)
-------------------------------------
Zaktualizuj plik `schemas.py`, dodając na dole klasę żądania dla transferu:

```python
from pydantic import Field # upewnij się, że masz ten import na górze
from decimal import Decimal

# --- Dodaj na dole pliku schemas.py ---
class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: Decimal = Field(..., gt=0.0, description="Kwota musi być większa od zera")
```

Krok 2: Endpoint Transferu z Blokadą Pesymistyczną (main.py)
------------------------------------------------------------
Dodaj odpowiednie importy i wklej nowy endpoint.
Inżynierski detal: 
Zauważ, jak sortujemy ID kont przed założeniem blokady. 
Jeśli Transakcja A przelewa z konta 1 na 2, a Transakcja B z 2 na 1, bez sortowania ID 
złapalibyśmy Deadlocka na poziomie bazy PostgreSQL. 
Zawsze blokujemy zasoby w spójnej kolejności!

```python
# --- 1. Biblioteki wbudowane w Pythona (Standard Library) ---
from contextlib import asynccontextmanager

# --- 2. Biblioteki zewnętrzne (Third-party) ---
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# --- 3. Moduły lokalne (Twoje własne pliki) ---
from database import Base, engine, get_db
from models import Account
from schemas import AccountCreate, AccountResponse, TransferRequest

# --- Dodaj na dole pliku main.py ---

@app.post("/transfer")
async def transfer_money(transfer: TransferRequest, db: AsyncSession = Depends(get_db)):
    if transfer.from_account_id == transfer.to_account_id:
        raise HTTPException(status_code=400, detail="Nie można przelać na to samo konto")

    # 1. Zabezpieczenie przed Deadlockiem: Sortujemy ID, żeby zawsze blokować wiersze w tej samej kolejności
    account_ids = sorted([transfer.from_account_id, transfer.to_account_id])

    try:
        # 2. PESSIMISTIC LOCKING: Odpowiednik @Lock(LockModeType.PESSIMISTIC_WRITE) ze Springa.
        # W bazie Postgres wywoła to: SELECT * FROM accounts WHERE id IN (...) FOR UPDATE;
        stmt = select(Account).where(Account.id.in_(account_ids)).with_for_update()
        result = await db.execute(stmt)
        
        # Wyciągamy konta i wrzucamy do słownika dla łatwego dostępu {id: obiekt}
        accounts = {acc.id: acc for acc in result.scalars().all()}

        # Walidacja istnienia kont
        if transfer.from_account_id not in accounts or transfer.to_account_id not in accounts:
            raise HTTPException(status_code=404, detail="Jedno z kont nie istnieje")

        from_account = accounts[transfer.from_account_id]
        to_account = accounts[transfer.to_account_id]

        # 3. Walidacja biznesowa
        if from_account.balance < transfer.amount:
            raise HTTPException(status_code=400, detail="Niewystarczające środki (Insufficient funds)")

        # 4. Operacja na danych (w pamięci)
        from_account.balance -= transfer.amount
        to_account.balance += transfer.amount

        # 5. Commit fizycznie zapisuje zmiany i ZWALNIA BLOKADY FOR UPDATE
        await db.commit()

        return {
            "status": "success",
            "from_account_balance": from_account.balance,
            "to_account_balance": to_account.balance
        }

    except HTTPException:
        # Puszczamy błędy biznesowe dalej (FastAPI samo je obsłuży)
        raise
    except Exception as e:
        # W razie jakiegokolwiek innego błędu (np. awaria sieci), wycofujemy transakcję
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Błąd wewnętrzny serwera: {str(e)}")
```


(Jeśli serwer działał przez docker-compose up, przeładuje się automatycznie).

Krok 3: Test Bojowy (Symulacja ataku współbieżnego)
---------------------------------------------------

Zrobimy zmasowany atak (DDoS) na Twój własny serwer. 
Utworzymy 50 wątków, które spróbują jednocześnie przelać pieniądze z konta nr 1 na konto nr 2.

Przygotowanie danych przez Swaggera `http://localhost:8000/docs`:

Użyj endpointu `POST /accounts`:
1. Stwórz konto nr 1 i zasil je kwotą 100.00
{
  "owner_name": "Jan Kowalski",
  "initial_balance": 100.00
}

2. Stwórz konto nr 2 i zasil je kwotą 0.00
{
  "owner_name": "Adam Nowak",
  "initial_balance": 0.00
}


Skrypt Atakujący (uruchom u siebie na Windowsie jako osobny plik):
Utwórz nowy plik `load_test.py` w swoim folderze i odpal go z terminala/PyCharma. 
Używa on puli wątków do strzelania w API.


```python
import requests
from concurrent.futures import ThreadPoolExecutor

URL = "http://localhost:8000/transfer"
PAYLOAD = {
    "from_account_id": 3,  #  -------> Uwaga, tutaj wpisz ID swojego konta nr 1 (Jan Kowalski)
    "to_account_id": 4,    #  -------> Uwaga, tutaj wpisz ID swojego konta nr 2 (Adam Nowak)
    "amount": 10.0  # Przelewamy 10 zł
}

def make_transfer():
    response = requests.post(URL, json=PAYLOAD)
    return response.status_code

print("Rozpoczynamy atak współbieżny: 50 przelewów naraz...")

# Tworzymy 50 wątków uderzających jednocześnie w serwer
with ThreadPoolExecutor(max_workers=50) as executor:
    # Uruchamiamy 50 żądań
    results = list(executor.map(lambda _: make_transfer(), range(50)))

# Podsumowanie
success = results.count(200)
failed = results.count(400)

print(f"Zakończono. Wyniki:")
print(f"✅ Udane przelewy (Status 200): {success}")
print(f"❌ Odrzucone przez brak środków (Status 400): {failed}")
```

Czego oczekujemy po teście?
---------------------------
Konto 1 ma 100 zł. 
Przelewamy po 10 zł.
Skrypt wysyła 50 żądań w tej samej milisekundzie.

Jeśli nie mielibyśmy `.with_for_update()`, większość wątków przeczytałaby saldo jako "100", 
wpuściła przelew i z konta wyparowałoby 500 zł (saldo na minus).

Z naszą blokadą pesymistyczną:
PostgreSQL kolejkuje żądania na poziomie sprzętowym. 
Tylko pierwsze 10 przelewów (10 x 10 zł = 100 zł) dostanie status 200 Success. 
Pozostałe 40 żądań musi poczekać w kolejce na zwolnienie blokady, 
odczyta zaktualizowane saldo (0 zł), 
uderzy w walidację i dostanie 400 Bad Request (Niewystarczające środki).

Odpal ten `load_test.py` i daj znać, czy wynik w konsoli zgadza się z teorią (10 udanych, 40 odrzuconych). 
To jest pełnoprawny, transakcyjny system klasy Enterprise!

Podsumowanie:
-------------

--- PODSUMOWANIE STATUSÓW ---
Status HTTP 400: wystąpił 40 razy
Status HTTP 200: wystąpił 10 razy
Process finished with exit code 0

BOOM! Mamy to!
--------------
Dokładnie taki wynik odróżnia systemy pisane na zaliczenie od prawdziwej architektury bankowej.

Co tu się właśnie wydarzyło (Podsumowanie Architekta):

Wysłałeś 50 wątków w tej samej milisekundzie.
Gdybyś napisał to w zwykłym skrypcie bez `.with_for_update()`, większość wątków weszłaby do funkcji widząc saldo 100.0. 
Przelewy przeszłyby jeden po drugim, a na koncie `Jan Kowalski` Id:3 zrobiłoby się minus 400 zł (słynny Lost Update).

Dzięki pesymistycznej blokadzie, Twój PostgreSQL zatrzasnął kłódkę na wierszach w tabeli. 
Pierwszy wątek zablokował konta, zrobił przelew, zwolnił kłódkę.
Kolejny wątek wszedł, zobaczył już 90.0 itd. 
Kiedy saldo spadło do 0.0, pozostałe 40 wątków uderzyło w ścianę walidacji i dostało kulturalne 400 Bad Request. 
Żadnych wyjątków w bazie, zero ujemnych sald.

Właśnie udowodniłeś, że Twój system spełnia rygorystyczne zasady `ACID` (Atomicity, Consistency, Isolation, Durability).
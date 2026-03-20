Lab7
----

Lab7--Projekt-Minibank--Konwersja-System-Walutowy-czyli-Multi-Currency-System
-----------------------------------------------------------------------------

W systemach bankowych walutę traktuje się jako atrybut konta (np. konto PLN, konto EUR). 
Konwersja to technicznie przelew z przewalutowaniem.

Architektura Inżynierska:
-------------------------
API Kursów Walut: 
Użyjemy darmowego API (np. exchangerate-api), żeby pobrać kursy "na żywo".

Transakcja Atomowa: 
Zanim zrobimy przelew, musimy "zamrozić" kurs waluty.

Obsługa Błędów: 
Co jeśli API walut nie działa? System musi odrzucić przelew (Safety First).

Krok 1: Model Konta (Aktualizacja - dodaj currency)
---------------------------------------------------

W `models.py` musisz wiedzieć, w jakiej walucie jest konto.

```python
class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_name: Mapped[str] = mapped_column(String(100), nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")  # ---------> Dodaj to pole!
    # Pole do blokad optymistycznych (@Version ze Springa)
    version: Mapped[int] = mapped_column(Integer, default=1)
```

Skoro w  models.py dodaliśmy kolumnę currency z domyślną wartością "PLN" do tabeli accounts.
Musimy teraz zaktualizować DTO w `schemas.py`.
Otwórz `schemas.py` i dodaj pole waluty do obiektów Request i Response:

```python
# W klasie AccountCreate dodaj:
class AccountCreate(BaseModel):
    owner_name: str = Field(..., min_length=2, max_length=100)
    initial_balance: Decimal = Field(default=Decimal('0.0'), ge=Decimal('0.0'))
    currency: str = Field(default="PLN", min_length=3, max_length=3) # <------------------- TO DODAJ

# W klasie AccountResponse dodaj:
class AccountResponse(BaseModel):
    id: int
    owner_name: str
    balance: Decimal
    currency: str  # <------------------- TO DODAJ
    model_config = ConfigDict(from_attributes=True)
```


oraz Zapisujmy walutę do bazy (main.py)
Znajdź endpoint create_account i przekaż walutę do modelu:

```python
@app.post("/accounts", response_model=AccountResponse, status_code=201)
async def create_account(account_in: AccountCreate, db: AsyncSession = Depends(get_db)):
    new_account = Account(
        owner_name=account_in.owner_name,
        balance=account_in.initial_balance,
        currency=account_in.currency.upper() # <--- TO DODAJ (od razu robimy wielkimi literami np. "USD")
    )
    # ... reszta bez zmian
```

Krok 2: Serwis Kursów (Nowy plik exchange.py)
---------------------------------------------
To jest serwis zewnętrzny. Izolujemy go od głównej logiki.

```python
import requests

def get_exchange_rate(from_curr, to_curr):
    # Używamy darmowego API (np. Frankfurter lub podobne)
    url = f"https://api.frankfurter.app/latest?from={from_curr}&to={to_curr}"
    response = requests.get(url)
    data = response.json()
    return data['rates'][to_curr]
```

Kiedy dodaliśmy plik exchange.py, użyliśmy biblioteki requests do komunikacji z zewnętrznym API. 
Ale Twój Docker nic o tym nie wie, bo przy budowaniu obrazu czyta tylko to, 
co masz wpisane w pliku requirements.txt.
W Springu to tak, jakbyś użył nowej klasy, ale zapomniał dodać jej do pom.xml.
Aktualizacja requirements.txt
Otwórz swój plik requirements.txt i dopisz na samym dole bibliotekę requests. 
Powinien teraz wyglądać tak:

```text
fastapi==0.110.0
uvicorn[standard]==0.27.1
sqlalchemy==2.0.28
asyncpg==0.29.0
pydantic==2.6.4
requests==2.31.0  # Dodaj tę linię do obecności biblioteki requests
```

Krok 3: Endpoint Konwersji (main.py)
------------------------------------
To jest "Złoty Endpoint". 
Wykonuje operacjęe:  `GET rate -> CALC -> TRANSFER`.

```python
from exchange import get_exchange_rate

# --- ENDPOINT: convert-transfer - tranzakcje walutowe (konwersje) ------------
@app.post("/convert-transfer")
async def convert_and_transfer(transfer: TransferRequest, db: AsyncSession = Depends(get_db)):
    # 1. Pobieramy konta
    ids = sorted([transfer.from_account_id, transfer.to_account_id])
    stmt = select(Account).where(Account.id.in_(ids)).with_for_update()
    result = await db.execute(stmt)
    accounts = {acc.id: acc for acc in result.scalars().all()}

    from_acc = accounts[transfer.from_account_id]
    to_acc = accounts[transfer.to_account_id]

    # 2. Pobieramy kurs walut
    try:
        if from_acc.currency == to_acc.currency:
            rate = 1.0  # Przelew w tej samej walucie
        else:
            rate = get_exchange_rate(from_acc.currency, to_acc.currency)
    except Exception as e:
        # Prawdziwy inżynier loguje takie rzeczy
        print(f"CRITICAL ERROR - Błąd API walutowego: {e}")
        raise HTTPException(status_code=502, detail=f"API walutowe niedostępne. Powód: {e}")

    # 3. Obliczamy kwotę docelową
    converted_amount = transfer.amount * Decimal(str(rate))

    # 4. Atomowa transakcja
    if from_acc.balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Brak środków")

    from_acc.balance -= transfer.amount
    to_acc.balance += converted_amount

    # 5. Historia
    history = TransactionHistory(
        from_account_id=from_acc.id,
        to_account_id=to_acc.id,
        amount=transfer.amount,
        note=f"Konwersja: {from_acc.currency} -> {to_acc.currency} (kurs: {rate})"
    )
    db.add(history)
    await db.commit()

    return {"status": "success", "rate_used": rate, "converted_amount": converted_amount}
```
Ponieważ dodaliśmy pole `note` do historii, musimy je teraz zdefiniować w modelu `TransactionHistory` (w models.py).
W systemach bankowych tytuł przelewu/notatka to i tak absolutny wymóg
Aktualizacja models.py
Otwórz models.py i dodaj kolumnę note do klasy TransactionHistory:

```python
# Upewnij się, że masz zaimportowany String z sqlalchemy
from sqlalchemy import String, Numeric, Integer, DateTime
from datetime import datetime

class TransactionHistory(Base):
    __tablename__ = "transactions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    from_account_id: Mapped[int] = mapped_column(Integer, nullable=False)
    to_account_id: Mapped[int] = mapped_column(Integer, nullable=False)
    # Zwiększamy też precyzję, żeby uniknąć błędu overflow z poprzednich labów
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    
    # DODAJEMY TĘ KOLUMNĘ:
    note: Mapped[str] = mapped_column(String(200), nullable=True) 
    
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```


Dlaczego to jest "Professional":
--------------------------------

Separation of Concerns: 
Logika API walutowego nie ma pojęcia o bazie danych. 
Logika bazy danych nie wie, skąd bierze się kurs. 
Dzięki temu kod jest testowalny (możesz przetestować `get_exchange_rate` osobno).

Decimal(str(rate)): 
Kluczowy moment! API zwraca float (np. 4.25345). 
W bankowości float to zło. 
Konwertujemy go na string, a potem na Decimal, żeby uniknąć błędów zaokrągleń w obliczeniach.

HTTP 502 (Bad Gateway): 
Jeśli API walutowe padnie, zwracamy błąd 502, co jest standardem REST dla problemów z zewnętrznymi serwisami.

Testowanie:
-----------

Opcja Nuklearna (Restart Bazy):
Ponieważ znów zmieniliśmy strukturę tabeli, a nie mamy narzędzia do migracji, musimy ubić wolumen bazy danych, 
żeby stworzyła się na nowo z kolumną note.

1. W terminalu wciśnij Ctrl+C.
2. Wpisz: `docker-compose down -v`
3. Wpisz: `docker-compose up --build`

 ...  i teraz testujemy odpalając Swaggera (http://localhost:8000/docs) lub Postmana:
1. Stwórz konto id=1 (PLN, 1000 PLN).
2. Stwórz konto id=2 (USD, 0 USD).
3. Wyślij `POST /convert-transfer` z kwotą 100 PLN.
4. Sprawdź salda: 
      - konto 1 powinno mieć 900 PLN
      - konto 2 powinno mieć ok. 25 USD (zależnie od kursu).

Działa? 
Czy potrzebujesz poprawki w modelu danych? 
Jak to przetestujesz, mamy kompletny system transakcyjny. 
Co robimy dalej? 
Zgodnie z planem: Automatyczne testy (pytest) czy może Frontend Angular?



Podsumowanie:
-------------

Masz w tym momencie kod na poziomie solidnego Mid/Senior Python Developera:
1. zbudowałeś asynchroniczny system transakcyjny (FastAPI + asyncpg)
2. zapakowałeś go w kontenery (Docker)
3. zabezpieczyłeś przed wyścigami (Pessimistic Locking)
4. zintegrowałeś z zewnętrznym API (przewalutowanie)
5. zachowaleś przy tym pełną spójność bazy danych (ACID)
6. 
Większość kursów z internetu nawet nie ociera się o takie problemy jak zablokowanie bazy, Decimal kontra float, czy zarządzanie pulą połączeń w lifespan.

Co robimy dalej?
----------------
Twój MiniBank backendowo jest gotowy. 
Wybierz, w którą stronę chcemy go teraz pchnąć (zgodnie z Twoim technologicznym stosem):

Opcja 1: Blokada Optymistyczna (Optimistic Locking - @Version)
--------------------------------------------------------------
Masz już w bazie kolumnę version. 
W systemach o ogromnym ruchu (np. giełda), pesymistyczne FOR UPDATE potrafi "zamulić" bazę, bo blokuje wiersze fizycznie. 
Nauczymy się, jak w SQLAlchemy aktualizować saldo bez blokowania bazy (sprawdzając wersję wiersza). 
To ulubione pytanie na rekrutacjach na architekta.

Opcja 2: Testy Automatyczne (Pytest)
------------------------------------
W Springu piszesz testy w `JUnit` - w Pythonie rządzie `pytest`. 
Napiszemy skrypt testowy, 
który sam postawi wirtualnego klienta, wyśle fałszywe żądania do Twojego API i sprawdzi, czy statusy to 200/400. 
Kod bez testów to tykająca bomba.


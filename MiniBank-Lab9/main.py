# --- 1. Biblioteki wbudowane (Standard Library) ---
import asyncio
import os
from contextlib import asynccontextmanager
from decimal import Decimal

# --- 2. Biblioteki zewnętrzne (Third-party) ---
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
# for Optimistic Locking
from sqlalchemy.orm.exc import StaleDataError

# --- 3. Moduły lokalne (Twoje własne pliki) ---
# Importy robimy w try/except — najpierw pakietowe (używane w testach),
# a jeśli uruchamiamy aplikację jako skrypt/moduł bez rodzica (np. w Dockerze
# uruchamiając `uvicorn main:app`) to wracamy do importów bez prefiksu.
try:
    from .database import AsyncSessionLocal, Base, engine, get_db
    from .exchange import get_exchange_rate
    from .models import Account, TransactionHistory
    from .schemas import AccountCreate, AccountResponse, AccountUpdate, TransferRequest
except Exception:
    from database import AsyncSessionLocal, Base, engine, get_db
    from exchange import get_exchange_rate
    from models import Account, TransactionHistory
    from schemas import AccountCreate, AccountResponse, AccountUpdate, TransferRequest


# --- LIFECYCLE: Tworzenie tabel w bazie przy starcie aplikacji ---
# W produkcji używa się migracji (Alembic/Flyway), ale do labów wystarczy to:
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Czekamy aż baza wstanie (retry logic)
    max_retries = 5
    for i in range(max_retries):
        try:
            # 1. Tworzymy tabele w bazie
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            break  # Jeśli się udało, wychodzimy z pętli
            # Po zakończeniu bloku `async with`, sesja automatycznie się zamyka
        except Exception as e:
            if i == max_retries - 1: raise e
            print(f"Baza danych jeszcze niegotowa, próba {i + 1}...")
            await asyncio.sleep(5)  # Czekamy 5 sekund i próbujemy znowu

    # 2. Tworzymy konto systemowe (ID 0), jeśli nie istnieje
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Account).filter_by(id=0))
        if not result.scalars().first():
            system_acc = Account(id=0, owner_name="SYSTEM", balance=Decimal("999999.00"))
            session.add(system_acc)
            await session.commit()
        # Po zakończeniu bloku `async with`, sesja automatycznie się zamyka
    yield  # Tu aplikacja działa

    # Tutaj możesz dodać kod zamykający (np. zamknięcie połączenia z bazą)
    # 3. CLEANUP: Kod zamykający
    print("Zamykanie serwera, czyszczenie zasobow...")
    # On some platforms/drivers (np. aiosqlite on Windows) disposing the engine
    # during TestClient teardown can cause a low-level access violation. To be
    # safe during local testing with SQLite we skip disposing the engine.
    try:
        db_url = os.environ.get("DATABASE_URL", "")
        if not db_url.startswith("sqlite"):
            await engine.dispose()
        else:
            print("Skipping engine.dispose() for SQLite (test run)")
    except Exception as e:
        print(f"Warning: error while disposing engine: {e}")

# Inicjalizacja aplikacji
app = FastAPI(title="MiniBank API", lifespan=lifespan)



# ------------------------------ ENDPOINTY -----------------------------------------

# --- ENDPOINT: Check health ---
@app.get("/health")
async def health_check():
    return {"status": "UP"}


# --- ENDPOINT: Utworzenie konta ---
# response_model mówi Swaggerowi, jakiego formatu JSON-a ma się spodziewać
@app.post("/accounts", response_model=AccountResponse, status_code=201)
async def create_account(
        account_in: AccountCreate,  # Springowe @RequestBody
        db: AsyncSession = Depends(get_db)  # Springowe @Autowired (Wstrzykiwanie sesji bazy)
):
    # Tworzymy encję na podstawie DTO
    new_account = Account(
        owner_name=account_in.owner_name,
        balance=account_in.initial_balance,
        currency=account_in.currency.upper()  # <--- TO DODAJ (od razu robimy wielkimi literami np. "USD")
    )

    # Zapis do bazy
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)  # Odświeżamy, żeby uzyskać nadane przez bazę ID

    return new_account


# --- ENDPOINT: READ: Pobierz wszystkie konta ---
@app.get("/accounts", response_model=list[AccountResponse])
async def get_all_accounts(db: AsyncSession = Depends(get_db)):
    # Wykonujemy zapytanie SELECT * FROM accounts
    result = await db.execute(select(Account))
    # scalars().all() wyciąga czyste obiekty Pythona z wyniku zapytania SQL
    return result.scalars().all()


# --- ENDPOINT: READ: Pobierz jedno konkretne konto ---
@app.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    account = await db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Konto o podanym ID nie istnieje")
    return account


# --- ENDPOINT: UPDATE: Aktualizacja danych konta (tylko nazwa właściciela) ---
@app.put("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(account_id: int, account_in: AccountUpdate, db: AsyncSession = Depends(get_db)):
    account = await db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Konto o podanym ID nie istnieje")

    # Aktualizujemy tylko dozwolone pola
    account.owner_name = account_in.owner_name

    await db.commit()
    await db.refresh(account)
    return account


# --- ENDPOINT: DELETE: Zamknięcie konta ---
# Używamy statusu 204 (No Content) - standard REST dla udanego usunięcia
@app.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db)):
    account = await db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Konto o podanym ID nie istnieje")

    # REGUŁA BIZNESOWA: Nie można usunąć konta, jeśli są na nim środki
    if account.balance > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Nie można zamknąć konta. Wypłać najpierw środki. Aktualne saldo: {account.balance}"
        )

    await db.delete(account)
    await db.commit()
    return None  # Przy 204 No Content nie zwracamy żadnego JSON-a




# --- ENDPOINT FINANSOWY: transfer money from/to acct:Id1 to acct:Id2 on the same acct currency ---
@app.post("/transfer")
async def transfer_money(transfer: TransferRequest, db: AsyncSession = Depends(get_db)):
    if transfer.from_account_id == transfer.to_account_id:
        raise HTTPException(status_code=400, detail="Nie można przelać na to samo konto")

    # 1. Zabezpieczenie przed Deadlockiem: Sortujemy ID, żeby zawsze blokować wiersze w tej samej kolejności
    account_ids = sorted([transfer.from_account_id, transfer.to_account_id])

    try:
        # 2. OPTIMISTIC LOCKING:
        # Pobieramy dane (brak blokady FOR UPDATE!)
        stmt = select(Account).where(Account.id.in_(account_ids))  # .with_for_update() --to bylo dla pesimistic locking
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

        # Zapis historii
        history = TransactionHistory(
            from_account_id=transfer.from_account_id,
            to_account_id=transfer.to_account_id,
            amount=transfer.amount,
            note=f"Transfer (Przelew optymistyczny): {from_account.balance} -> {to_account.balance}"
        )
        db.add(history)

        # 4. PRÓBA ZAPISU Z OCC
        try:
            # SQLAlchemy wyśle do bazy: UPDATE ... WHERE id=X AND version=1
            # Flush first to surface StaleDataError early, then commit
            await db.flush()
            await db.commit()
            return {
                "status": "success",
                "from_account_balance": from_account.balance,
                "to_account_balance": to_account.balance
            }
        except StaleDataError:
            await db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Konflikt danych. Saldo konta zmieniło się w międzyczasie. Spróbuj ponownie."
            )

    except HTTPException:
        # Puszczamy błędy biznesowe dalej (FastAPI samo je obsłuży)
        raise
    except Exception as e:
        # W razie jakiegokolwiek innego błędu (np. awaria sieci), wycofujemy transakcję
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Błąd wewnętrzny serwera: {str(e)}")




# DTO dla wszystkich operacji
class TransactionRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: Decimal


# --- ENDPOINT FINANSOWY: transaction - czyli operacje: dodawania, odejmowania salda z/do konta Specjalnego ------------
@app.post("/transaction")
# Zakładam, że TransactionRequest, Account, TransactionHistory i get_db są zdefiniowane gdzie indziej.
async def execute_transaction(tx: 'TransactionRequest', db: AsyncSession = Depends(get_db)):
    # 1) Sortujemy ID, żeby zapobiegać deadlockom
    ids = sorted([tx.from_account_id, tx.to_account_id])

    try:
        # 2) OPTIMISTIC LOCKING - zwykły select (bez with_for_update)
        stmt = select(Account).where(Account.id.in_(ids))
        result = await db.execute(stmt)
        accounts = {acc.id: acc for acc in result.scalars().all()}

        # 3) Walidacja istnienia kont oraz dostępności środków (konto 0 = SYSTEM może być na minusie)
        if tx.from_account_id not in accounts or tx.to_account_id not in accounts:
            raise HTTPException(status_code=404, detail="Konto nie istnieje")

        from_acc = accounts[tx.from_account_id]
        to_acc = accounts[tx.to_account_id]

        if from_acc.balance < tx.amount and from_acc.id != 0:
            raise HTTPException(status_code=400, detail="Brak środków")

        # 4) Zmiana sald w pamięci i zapis historii
        from_acc.balance -= tx.amount
        to_acc.balance += tx.amount

        history = TransactionHistory(
            from_account_id=tx.from_account_id,
            to_account_id=tx.to_account_id,
            amount=tx.amount,
            note=f"Transaction (Przelew optymistyczny): {from_acc.balance} -> {to_acc.balance})"
        )
        db.add(history)

        # 5) Próba zapisu: jeśli wersja w bazie się zmieni (konflikt), SQLAlchemy rzuci StaleDataError
        try:
            await db.flush()
            await db.commit()
            return {"status": "success"}
        except StaleDataError:
            await db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Konflikt danych. Saldo konta zmieniło się w międzyczasie. Spróbuj ponownie."
            )

    except HTTPException:
        # Przepuszczamy błędy biznesowe dalej
        raise
    except Exception as e:
        # Inne nieoczekiwane błędy -> rollback + 500
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Błąd wewnętrzny serwera: {e}")



# --- ENDPOINT FINANSOWY: convert-transfer - tranzakcje walutowe (konwersje) ------------
@app.post("/convert-transfer")
async def convert_and_transfer(transfer: TransferRequest, db: AsyncSession = Depends(get_db)):
    # 1. Pobieramy konta
    ids = sorted([transfer.from_account_id, transfer.to_account_id])

    # Zdejmujemy kłódkę! Zamiast with_for_update() używamy zwykłego selecta
    stmt = select(Account).where(Account.id.in_(ids))  # .with_for_update()

    result = await db.execute(stmt)
    accounts = {acc.id: acc for acc in result.scalars().all()}

    from_acc = accounts.get(transfer.from_account_id)
    to_acc = accounts.get(transfer.to_account_id)

    if not from_acc or not to_acc:
        raise HTTPException(status_code=404, detail="Konto nie istnieje")

    # 2. Pobieramy kurs walut
    try:
        if from_acc.currency == to_acc.currency:
            rate = 1.0  # Przelew w tej samej walucie
        else:
            rate = get_exchange_rate(from_acc.currency, to_acc.currency)
    except Exception as e:
        # Tu logujemy takie rzeczy
        print(f"CRITICAL ERROR - Błąd API walutowego: {e}")
        raise HTTPException(status_code=502, detail=f"API walutowe niedostępne. Powód: {e}")

    # 3. Obliczamy kwotę docelową
    converted_amount = transfer.amount * Decimal(str(rate))

    # 4. Atomowa transakcja
    if from_acc.balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Brak środków")

    from_acc.balance -= transfer.amount
    to_acc.balance += converted_amount

    history = TransactionHistory(
        from_account_id=from_acc.id,
        to_account_id=to_acc.id,
        amount=transfer.amount,
        note = f"Konwersja (Przelew optymistyczny): {from_acc.currency} -> {to_acc.currency} (kurs: {rate})"
    )
    db.add(history)

    # 5. KLUCZOWY MOMENT: Próba zapisu
    try:
        # Tu SQLAlchemy wysyła zapytanie:
        # UPDATE accounts SET balance=..., version=2 WHERE id=1 AND version=1
        await db.flush()
        await db.commit()
    except StaleDataError:
        # Jeśli inny proces w międzyczasie zmienił wersję, wpadamy tutaj!
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Konflikt danych (Race Condition). Saldo konta zostało zmienione w innej transakcji. Spróbuj ponownie."
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "success"}
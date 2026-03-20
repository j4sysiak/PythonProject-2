import asyncio  # Dodaj to na samej górze
import time

# --- 1. Biblioteki wbudowane w Pythona (Standard Library) ---
from contextlib import asynccontextmanager
from decimal import Decimal

# --- 2. Biblioteki zewnętrzne (Third-party) ---
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# --- 3. Moduły lokalne (Twoje własne pliki) ---
from database import Base, engine, get_db, AsyncSessionLocal
from models import Account, TransactionHistory
from schemas import AccountCreate, AccountResponse, TransferRequest, AccountUpdate

from database import Base


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
            system_acc = Account(id=0, owner_name="SYSTEM", balance=999999.0)
            session.add(system_acc)
            await session.commit()
        # Po zakończeniu bloku `async with`, sesja automatycznie się zamyka
    yield  # Tu aplikacja działa

    # Tutaj możesz dodać kod zamykający (np. zamknięcie połączenia z bazą)
    # 3. CLEANUP: Kod zamykający
    print("Zamykanie serwera, czyszczenie zasobów...")
    await engine.dispose() # To jest kluczowe! Zamyka pulę połączeń do bazy

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
        balance=account_in.initial_balance
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


# --- ENDPOINT: transfer money ------------
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

        # Zapis historii
        history = TransactionHistory(
            from_account_id=transfer.from_account_id,
            to_account_id=transfer.to_account_id,
            amount=transfer.amount
        )
        db.add(history)

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


# DTO dla wszystkich operacji
class TransactionRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: Decimal


@app.post("/transaction")
async def execute_transaction(tx: TransactionRequest, db: AsyncSession = Depends(get_db)):
    # 1. Sortowanie ID (ochrona przed Deadlockiem)
    ids = sorted([tx.from_account_id, tx.to_account_id])

    # 2. Blokada pesymistyczna na oba konta naraz
    stmt = select(Account).where(Account.id.in_(ids)).with_for_update()
    result = await db.execute(stmt)
    accounts = {acc.id: acc for acc in result.scalars().all()}

    # 3. Walidacja biznesowa
    if tx.from_account_id not in accounts or tx.to_account_id not in accounts:
        raise HTTPException(status_code=404, detail="Konto nie istnieje")

    from_acc = accounts[tx.from_account_id]
    to_acc = accounts[tx.to_account_id]

    if from_acc.balance < tx.amount and from_acc.id != 0:  # Systemowe konto (0) może mieć debet
        raise HTTPException(status_code=400, detail="Brak środków")

    # 4. Atomowa operacja
    from_acc.balance -= tx.amount
    to_acc.balance += tx.amount

    history = TransactionHistory(
        from_account_id=tx.from_account_id,
        to_account_id=tx.to_account_id,
        amount=tx.amount
    )
    db.add(history)
    await db.commit()
    return {"status": "success"}
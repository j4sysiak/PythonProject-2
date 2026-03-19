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

# --- LIFECYCLE: Tworzenie tabel w bazie przy starcie aplikacji ---
# W produkcji używa się migracji (Alembic/Flyway), ale do labów wystarczy to:
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# Inicjalizacja aplikacji
app = FastAPI(title="MiniBank API", lifespan=lifespan)


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
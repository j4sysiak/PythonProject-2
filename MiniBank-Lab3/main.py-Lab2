# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import engine, Base, get_db
from models import Account
from schemas import AccountCreate, AccountResponse


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
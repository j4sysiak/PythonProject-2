Lab2--Projekt-Minibank--Warstwa-Danych-Entity-DTO-Dependency-Injection
----------------------------------------------------------------------

W Javie/Springu zrobiłbyś teraz:
1. `@Entity`
2. klasę `DTO`
3. klasę `Repository`
4. klasę `@Service`

W Pythonie `FastAPI` zrobimy to w sposób nowocześniejszy i lżejszy. 
Użyjemy:
1. `SQLAlchemy 2.0` (odpowiednik Hibernate) do mapowania obiektowo-relacyjnego. 
2. Pydantic do walidacji danych i DTO.

Stwórz w swoim folderze MiniBank trzy nowe pliki.

Krok 1: Konfiguracja połączenia z bazą (database.py) - plik 1/3
---------------------------------------------------------------
To odpowiednik konfiguracji `DataSource w Springu`. 
Tworzymy silnik asynchroniczny, bo nie chcemy blokować wątków (jak w tradycyjnym `JDBC`).

```python
# database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Pobieramy URL z docker-compose.yml (Environment variables)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://bank_admin:superhaslo123@db:5432/minibank")

# Tworzymy asynchroniczny silnik bazy danych
engine = create_async_engine(DATABASE_URL, echo=True) # echo=True wypisuje czysty SQL w konsoli

# Fabryka sesji (odpowiednik EntityManagerFactory)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Klasa bazowa, z której będą dziedziczyć wszystkie nasze tabele
Base = declarative_base()

# Funkcja dostarczająca sesję do bazy (użyjemy jej jako wstrzykiwania zależności)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

Krok 2: Encje Bazy Danych (models.py) - plik 2/3
------------------------------------------------
Definiujemy strukturę tabeli. 
Zwróć uwagę na pole `version` – użyjemy go w Lab 3 do Optymistycznego Blokowania (Optimistic Locking), 
żeby dwa systemy naraz nie zmodyfikowały salda.

```python
# models.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Numeric, Integer
from database import Base

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_name: Mapped[str] = mapped_column(String(100), nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    
    # Pole do blokad optymistycznych (@Version ze Springa)
    version: Mapped[int] = mapped_column(Integer, default=1)
```

Krok 3: DTO i Walidacja (schemas.py) - plik 3/3
-----------------------------------------------
W Springu piszesz klasy z `@NotNull`, `@Min(0)` itd. 
Tutaj używamy biblioteki `Pydantic`. 
Klasy z tego pliku służą TYLKO do komunikacji z `API` (żądania i odpowiedzi). 
Nie mają pojęcia o bazie danych.

```python
# schemas.py
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal

# DTO dla tworzenia konta (Request)
class AccountCreate(BaseModel):
    owner_name: str = Field(..., min_length=2, max_length=100, description="Imię i nazwisko właściciela")
    initial_balance: Decimal = Field(default=0.0, ge=0.0, description="Początkowy depozyt")

# DTO dla zwracania konta (Response)
class AccountResponse(BaseModel):
    id: int
    owner_name: str
    balance: Decimal

    # Pozwala Pydanticowi czytać dane bezpośrednio z obiektów SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
```

Krok 4: Integracja w kontrolerze (main.py)
------------------------------------------
Teraz łączymy to wszystko w głównym pliku. 
Nadpisz swój main.py:

```python
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
    account_in: AccountCreate, # Springowe @RequestBody
    db: AsyncSession = Depends(get_db) # Springowe @Autowired (Wstrzykiwanie sesji bazy)
):
    # Tworzymy encję na podstawie DTO
    new_account = Account(
        owner_name=account_in.owner_name,
        balance=account_in.initial_balance
    )
    
    # Zapis do bazy
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account) # Odświeżamy, żeby uzyskać nadane przez bazę ID
    
    return new_account
```

Inżynierskie podsumowanie (Co tu się wydarzyło):
------------------------------------------------
Depends(get_db): 
To jest system Dependency Injection (DI) we Flasku/FastAPI. 
Kiedy przychodzi zapytanie (`Request`), `FastAPI`:
1. odpala funkcję get_db()
2. otwiera transakcję do bazy
3. przekazuje Ci ją do zmiennej db
4. po zakończeniu requestu (w bloku finally, który zdefiniowaliśmy w yield) samoczynnie i bezpiecznie zamyka połączenie.

Walidacja: 
Jeśli ktoś spróbuje wysłać JSON-a z ujemnym balansem, `Pydantic` automatycznie wyrzuci piękny błąd 422 Unprocessable Entity. 
Twój kod w ogóle się nie wykona. 
Brama bezpieczeństwa.

Przetestuj to:
-----------------
1. Zapisz pliki. 
2. Serwer w Dockerze powinien sam wykryć zmiany i się zrestartować (zobaczysz logi w terminalu).
3. Odśwież w przeglądarce http://localhost:8000/docs 
4. Zobaczysz nowy endpoint POST `/accounts` z opisem i modelem danych.

Kliknij w niego -> `Try it out` -> `Execute` i zobacz, że w `Request body` pojawił się szablon JSON-a do wypełnienia.

Wpisz jakiegoś JSON-a, np:

```json
{
  "owner_name": "Jan Kowalski",
  "initial_balance": 1000.50
}
```


Kliknij Execute.
Powinieneś dostać status 201 i JSON-a z wygenerowanym numerem id: 1.

jak podejrzeć bazę danych?
-----------------
1. Pobierz i zainstaluj `pgAdmin` (graficzny klient do Postgresa).
2. Połącz się z bazą, używając danych z `docker-compose.yml`:
   - Host: localhost
   - Port: 5433
   - Username: bank_admin
   - Password: superhaslo123  
   - Database: minibank
3. Połącz się i zobacz, że tabela `accounts` została utworzona, a w niej jest rekord z Janem Kowalskim i jego saldem.


Daj znać, czy przeszedłeś ten test.
Jeśli tak, w Lab 3 zrobimy transfery między kontami (/transfer) z symulacją problemów ze współbieżnością (Concurrent requests) 
i użyjemy mechanizmu blokady.


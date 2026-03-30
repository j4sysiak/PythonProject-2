# database.py
# Tworzy silnik (engine) i sesję (session) do bazy danych,
# korzystając z URL-a podanego w zmiennej środowiskowej DATABASE_URL.
# Używamy SQLAlchemy z asyncpg dla asynchronicznej komunikacji z Postgresem.
# Klasa Base jest bazą dla naszych modeli (tabel).
# Funkcja get_db() jest generatorem, który dostarcza sesję do bazy danych
# i jest używana jako wstrzykiwanie zależności w FastAPI.

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
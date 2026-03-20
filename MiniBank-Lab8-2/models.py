# models.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Numeric, Integer, DateTime
from database import Base
from datetime import datetime

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_name: Mapped[str] = mapped_column(String(100), nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")
    # Pole do blokad optymistycznych (@Version ze Springa)
    version: Mapped[int] = mapped_column(Integer, default=1)

class TransactionHistory(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_account_id: Mapped[int] = mapped_column(Integer, nullable=False)
    to_account_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Zwiększamy też precyzję, żeby uniknąć błędu overflow z poprzednich labów
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)

    # DODAJEMY TĘ KOLUMNĘ do obsługi konwersji walutowych:
    note: Mapped[str] = mapped_column(String(200), nullable=True)

    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)
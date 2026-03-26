# models.py
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Numeric, Integer, DateTime

try:
    from .database import Base
except Exception:
    from database import Base

from datetime import datetime, timezone




class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Use Decimal for monetary values to avoid floating point issues
    balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")

    # Pole do blokad optymistycznych (@Version ze Springa)
    version: Mapped[int] = mapped_column(Integer, default=1)

    # --- TO JEST ODPOWIEDNIK @Version ze Spring ---
    __mapper_args__ = {
        "version_id_col": version # SQLAlchemy będzie pilnować tego pola!
    }




class TransactionHistory(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_account_id: Mapped[int] = mapped_column(Integer, nullable=False)
    to_account_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Zwiększamy też precyzję, żeby uniknąć błędu overflow z poprzednich labów
    # Store amounts as Decimal
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    # DODAJEMY TĘ KOLUMNĘ do obsługi konwersji walutowych:
    note: Mapped[str] = mapped_column(String(200), nullable=True)

    # Use timezone-aware UTC timestamps (TIMESTAMP WITH TIME ZONE in Postgres)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

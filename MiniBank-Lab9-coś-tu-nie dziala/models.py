# models.py
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Numeric, Integer
from .database import Base
from datetime import datetime, timezone
from pydantic import BaseModel
from decimal import Decimal

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


# DTO dla wszystkich operacji
class TransactionRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: Decimal

    class Config:
        orm_mode = True


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

    # Use timezone-aware UTC timestamps
    timestamp: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

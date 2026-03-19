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
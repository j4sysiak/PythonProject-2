Lab5--Projekt-Minibank--Historia-Transakcji--Relacje--Tabele--ACID-w-praktyce
-----------------------------------------------------------------------------

`ACID` (Atomicity, Consistency, Isolation, Durability) to serce bankowości. 
Skoro masz już działający `CRUD`, teraz musimy sprawić, żeby "przelew" był niepodzielną operacją.

Atomowość
---------
Jeśli w trakcie przelewu padnie serwer (np. prąd zgaśnie po odjęciu kasy z konta A, ale przed dodaniem do konta B), 
baza musi automatycznie cofnąć wszystko. 
To jest Atomowość.

Krok 1: Model Historii (models.py)
----------------------------------
Musimy wiedzieć, kto, komu, kiedy i ile przelał. 
Dodaj tę klasę do `models.py`:

```python
from datetime import datetime

class TransactionHistory(Base):
    __tablename__ = "transactions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    from_account_id: Mapped[int] = mapped_column(Integer, nullable=False)
    to_account_id: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

Krok 2: Endpoint Transferu z ACID (main.py)
-------------------------------------------
To jest najważniejszy kod w całym projekcie. 
Używamy tu jednej transakcji bazodanowej dla trzech operacji (odjęcie, dodanie, zapis historii).

```python
from models import Account, TransactionHistory

@app.post("/transfer")
async def transfer_money(transfer: TransferRequest, db: AsyncSession = Depends(get_db)):
    # 1. Sortowanie ID (zabezpieczenie przed Deadlockiem)
    ids = sorted([transfer.from_account_id, transfer.to_account_id])
    
    # 2. Blokada PESSIMISTIC (FOR UPDATE) - nikt inny nie dotknie tych kont do końca tej transakcji
    stmt = select(Account).where(Account.id.in_(ids)).with_for_update()
    result = await db.execute(stmt)
    accounts = {acc.id: acc for acc in result.scalars().all()}

    # ... [tu Twoja walidacja z poprzedniego kodu] ...
    
    # 3. OPERACJA ATOMOWA: Jeśli coś się wysypie w trakcie, db.rollback() cofa wszystko
    try:
        from_acc.balance -= transfer.amount
        to_acc.balance += transfer.amount
        
        # Zapis historii
        history = TransactionHistory(
            from_account_id=transfer.from_account_id,
            to_account_id=transfer.to_account_id,
            amount=transfer.amount
        )
        db.add(history)
        
        # JEDEN COMMIT dla wszystkiego!
        await db.commit()
        return {"status": "success"}
        
    except Exception:
        await db.rollback() # Wycofanie zmian w razie błędu
        raise HTTPException(status_code=500, detail="Błąd transakcji, środki nie zostały pobrane.")
```

Krok 3: Test spójności danych
-----------------------------
Zrób przelew z konta A do konta B. `post("/transfer")` - z Swaggera lub Postmana.
Po zrobieniu przelewu, sprawdź w swoim DB Browser for SQLite (lub w Postgresie):
1. Czy saldo konta A się zmniejszyło?
2. Czy saldo konta B się zwiększyło?
3. Czy w tabeli transactions pojawił się nowy wiersz?


Masz już solidne fundamenty.:
-----------------------------
1. API (FastAPI) – szybkie i nowoczesne. 
2. Bazy Danych (SQLAlchemy + Postgres) – bezpieczne i ACID. 
3. Logikę Biznesową – z blokadami (FOR UPDATE). 
4. Dokumentację – automatyczny Swagger pod /docs.

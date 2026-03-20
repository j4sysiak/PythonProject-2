Lab6
----

Lab6--Projekt-Minibank--Operacje-finansowe
------------------------------------------

W tej części projektu skupimy się na implementacji operacji finansowych, takich jak przelewy między kontami.
To jest "Finansowy Fundament". 
Jeśli chcesz budować system bankowy, nie możesz mieć osobnych endpointów dla transfer, deposit i withdraw.
Inżynierowie bankowi używają `Wzorca Komendy (Command Pattern)` lub `Operacji Atomowych`. 
Każda z tych trzech akcji to w istocie `Przelew`
(Depozyt to przelew z system_account na twoje_konto, Wypłata to przelew z twojego_konta na system_account).

Zaimplementujemy to tak, aby wszystko szło przez jeden, bezpieczny mechanizm transakcyjny.

Krok 1: Dodaj konto systemowe w bazie (w main.py)
-------------------------------------------------
Przy starcie aplikacji dodaj konto "Systemowe" o ID = 0. 
Ono będzie źródłem wszystkich wpłat i miejscem wypłat.

```python
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
    yield  # Tu aplikacja działa
    # Tutaj możesz dodać kod zamykający (np. zamknięcie połączenia z bazą)
```

Krok 2: Jeden "Bóg" operacji finansowych (main.py)
--------------------------------------------------
Zamiast pisać 3 osobne endpointy, zrobimy jedną funkcję execute_transaction, która obsługuje wszystko. 
Dzięki temu kod nie będzie się duplikował, a blokada `FOR UPDATE` zadziała wszędzie tak samo.

```python
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

    if from_acc.balance < tx.amount and from_acc.id != 0: # Systemowe konto (0) może mieć debet
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
```

Krok 3: Jak używać tego systemu (Biznesowo):
--------------------------------------------
Teraz Twoje "trzy funkcje" to tylko różna kolejność ID:

Wpłata (Deposit): 
from_account_id: 0, to_account_id: Twoje_ID, amount: 500. (Kasa leci z systemu do Ciebie).

Wypłata (Withdrawal): 
from_account_id: Twoje_ID, to_account_id: 0, amount: 200. (Kasa leci od Ciebie do systemu).

Transfer: 
from_account_id: 
Twoje_ID, to_account_id: Kumpla_ID, amount: 100.

Krok 4: Konwersje (Opcjonalnie)
Jeśli chcesz konwersje walut (np. PLN na USD), to jest to osobna logika "Kurs Waluty".

Inżynierski krok: Pobierasz aktualny kurs z API (np. NBP).
Obliczasz: amount_in_pln = amount_in_usd * kurs.
Wołasz execute_transaction z amount_in_pln.


Dlaczego to jest lepsze niż 3 osobne endpointy?
-----------------------------------------------

DRY (Don't Repeat Yourself): 
Logikę sprawdzania blokad, zapisu do historii i atomowości commit/rollback masz w jednym miejscu. 
Jak znajdziesz buga, poprawiasz go raz, a nie w trzech plikach.

Spójność (Consistency): 
Masz gwarancję, że każda operacja finansowa w banku przechodzi przez ten sam "młynek" walidacji.

Test:
Czy taka "uniwersalna metoda przelewu" z kontem systemowym 0 ma dla Ciebie sens? 
Jeśli tak – masz fundament banku. 
Jeśli chcesz, dodamy teraz Konwersje Walut z zewnętrznego API NBP, żebyś zobaczył, jak łączyć przeliczenia z transakcjami. Robimy to?  


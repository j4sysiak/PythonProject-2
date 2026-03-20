Lab4--Projekt-Minibank--full-CRUD
---------------------------------

Zrobimy teraz Pełny `CRUD` (Create, Read, Update, Delete) dla kont bankowych.
Musisz mieć pełną kontrolę nad zasobami. 
W Springu to byłby standardowy `AccountController` z pełnym zestawem metod.

W systemach finansowych nie można tak po prostu "usunąć" konta, 
jeśli są na nim pieniądze, ani zmienić salda zwykłym PUT (od salda są przelewy). 
Dlatego nasz CRUD będzie miał wbudowane reguły biznesowe.

Krok 1: DTO dla aktualizacji (schemas.py)
-----------------------------------------
Nie chcemy, żeby ktoś przez endpoint PUT mógł zmienić swoje saldo na milion. 
Pozwolimy tylko na zmianę nazwy właściciela.

Otwórz schemas.py i dodaj na dole:
----------------------------------

````python
# DTO dla aktualizacji konta (Update)
class AccountUpdate(BaseModel):
    owner_name: str = Field(..., min_length=2, max_length=100, description="Nowe imię i nazwisko właściciela")
````

Krok 2: Endpointy R-U-D (main.py)
---------------------------------
Masz już `POST /accounts (Create)`. Teraz dodamy brakujące klocki.
Zwróć uwagę na to, jak w `FastAPI` zwraca się listy `list[AccountResponse]` i jak używamy asynchronicznego `db.get()`.

Otwórz main.py i wklej te endpointy (np. pod Twoim istniejącym `POST /accounts`, a przed `/transfer`):

```python
# --- READ: Pobierz wszystkie konta ---
@app.get("/accounts", response_model=list[AccountResponse])
async def get_all_accounts(db: AsyncSession = Depends(get_db)):
    # Wykonujemy zapytanie SELECT * FROM accounts
    result = await db.execute(select(Account))
    # scalars().all() wyciąga czyste obiekty Pythona z wyniku zapytania SQL
    return result.scalars().all()


# --- READ: Pobierz jedno konkretne konto ---
@app.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(account_id: int, db: AsyncSession = Depends(get_db)):
    account = await db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Konto o podanym ID nie istnieje")
    return account


# --- UPDATE: Aktualizacja danych konta (tylko nazwa właściciela) ---
@app.put("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(account_id: int, account_in: AccountUpdate, db: AsyncSession = Depends(get_db)):
    account = await db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Konto o podanym ID nie istnieje")
    
    # Aktualizujemy tylko dozwolone pola
    account.owner_name = account_in.owner_name
    
    await db.commit()
    await db.refresh(account)
    return account


# --- DELETE: Zamknięcie konta ---
# Używamy statusu 204 (No Content) - standard REST dla udanego usunięcia
@app.delete("/accounts/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: int, db: AsyncSession = Depends(get_db)):
    account = await db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Konto o podanym ID nie istnieje")
    
    # REGUŁA BIZNESOWA: Nie można usunąć konta, jeśli są na nim środki
    if account.balance > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Nie można zamknąć konta. Wypłać najpierw środki. Aktualne saldo: {account.balance}"
        )
        
    await db.delete(account)
    await db.commit()
    return None # Przy 204 No Content nie zwracamy żadnego JSON-a
```

Inżynierskie Smaczki (FastAPI vs Spring):
-----------------------------------------
Zmienne w URL: 
Zauważ ścieżkę `/accounts/{account_id}`. 
W argumencie funkcji piszesz po prostu `account_id: int`. 
FastAPI samo wie (odpowiednik `@PathVariable` w Springu), żeby wyciągnąć to z urla, i automatycznie sprawdza, czy to jest liczba. 
Jak ktoś wpisze /accounts/jacek, FastAPI odrzuci to ze statusem 422 Unprocessable Entity bez ani jednej linijki Twojego kodu.

list[AccountResponse]: 
Pydantic jest genialny. 
Jak powiesz mu, że zwracasz listę takich obiektów, on sam przeleci przez wynik z bazy, 
zamieni każdy z nich na JSON-a i wypluje gotową tablicę.

Status 204 No Content: 
Kiedy usuwasz zasób w architekturze `REST`, dobrą praktyką jest nie zwracać niczego w ciele (body) odpowiedzi, 
stąd użycie tego konkretnego statusu.


Przetestuj swój nowy ekwipunek:
-------------------------------
1. Zapisz pliki (Docker przeładuje serwer w sekundę).
2. Wejdź na Swaggera: `http://localhost:8000/docs` - Zobaczysz tam piękną sekcję z pełnym CRUD-em dla kont.

Zrób testy:
-----------
Odpal `GET /accounts` (zobaczysz listę swoich kont).

Zrób `PUT /accounts/1` (zmień imię na "Jacek Nowak").

Zrób `DELETE /accounts/1` (spróbuj usunąć konto, na którym masz 100 zł z poprzedniego testu 
            – powinieneś dostać blokadę biznesową i status 400).

Stwórz nowe konto z saldem 0.0 i spróbuj je usunąć (powinno zniknąć, status 204).

Działa jak w szwajcarskim banku? 
Jeśli tak, masz solidny fundament obiektowy. 
Zgodnie z Twoim życzeniem, po opanowaniu tego, możemy wjechać w Opcję A: Historia Transakcji (Relacje, tabele i ACID w praktyce).


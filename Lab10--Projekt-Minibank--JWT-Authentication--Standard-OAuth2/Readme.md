Lab10
-----

Lab10--Projekt-Minibank--JWT-Authentication--Standard-OAuth2
------------------------------------------------------------

Wchodzimy w świat FastAPI Security. 
Jako człowiek od Spring Boota poczujesz się tu jak w domu, ale docenisz brak tysiąca linii XML-a 
czy adnotacji ukrytych głęboko w frameworku.

W Pythonie nie mamy ogromnego "Spring Security". 
Mamy za to `Dependency Injection`, które służy jako "strażnik" (Guard). 
Jeśli funkcja nie dostanie poprawnego tokena, `Dependency` rzuci wyjątek, a kod endpointu w ogóle się nie wykona.

Krok 1: Instalacja paczek kryptograficznych
-------------------------------------------
W terminalu (środowisko lokalne) zainstaluj narzędzia do haszowania haseł i obsługi tokenów:
`pip install "python-jose[cryptography]" "passlib[bcrypt]" python-multipart`

Krok 1.5: Dopisz nowe paczki do swojego requirements.txt 
--------------------------------------------------------
Musisz dopisać trzy kluczowe paczki, które odpowiadają za "bebechy" bezpieczeństwa. 
1. python-jose[cryptography]
2. passlib[bcrypt]
3. python-multipart

Bez nich kontener Dockerowy wywali się przy próbie importu bibliotek kryptograficznych.
Oto jak powinien wyglądać Twój kompletny i zaktualizowany plik requirements.txt

```text
# --- Podstawa API ---
fastapi
uvicorn[standard]
pydantic
requests

# --- Baza danych (Async) ---
sqlalchemy
asyncpg

# --- NOWOŚĆ: Bezpieczeństwo i JWT ---
python-jose[cryptography]
passlib[bcrypt]
python-multipart

# --- Testowanie (z Labów 6/7) ---
pytest
pytest-asyncio
httpx
testcontainers
```

Dlaczego akurat te trzy? (Inżynierskie wyjaśnienie):
----------------------------------------------------
python-jose[cryptography]: 
To odpowiednik biblioteki jjwt lub nimbus-jose-jwt w Javie. 
Zajmuje się generowaniem, podpisywaniem i weryfikacją tokenów JWT. 
Rozszerzenie [cryptography] instaluje silnik do szyfrowania (kluczowy przy algorytmie HS256).

passlib[bcrypt]: 
To standardowy mechanizm haszowania. 
W Spring Security używasz `BCryptPasswordEncoder`. 
W Pythonie używamy `passlib`, która zajmuje się "soleniem" haseł i sprawdzaniem ich poprawności.

python-multipart: 
To jest często pomijany element. 
Standard `OAuth2` (używany przez `FastAPI w Swaggerze`) przesyła login i hasło jako `Form Data`, a nie jako `JSON`. 
`FastAPI` potrzebuje tej paczki, żeby móc sparsować dane przysłane z formularza logowania.


Krok 2: Serwis Bezpieczeństwa (auth.py)
---------------------------------------
To będzie Twój odpowiednik `PasswordEncoder` i `JwtService`. 
Tworzymy nowy plik `auth.py`.

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# Konfiguracja - w produkcji trzymaj to w zmiennych środowiskowych!
SECRET_KEY = "TWOJ_BARDZO_TAJNY_KLUCZ_DO_GENEROWANIA_TOKENOW"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Kontekst haszowania (używamy Bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

Krok 3: Relacja Użytkownik -> Konto (models.py)
-----------------------------------------------
W prawdziwym banku nie ma kont "anonimowych". 
Musimy połączyć `User` z `Account`.
(Użyjemy tabeli `User`, którą stworzyliśmy we `Flasku`, ale teraz w czystym SQLAlchemy 2.0).

```python
# models.py
from decimal import Decimal

from sqlalchemy import String, Numeric, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Twoja klasa bazowa z database.py
try:
    from .database import Base
except Exception:
    from database import Base

from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(200))

    # RELACJA: Jeden user ma wiele kont
    # "Account" w cudzysłowie, żeby uniknąć błędu kołowego importu
    accounts: Mapped[list["Account"]] = relationship("Account", back_populates="owner")


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

    # KLUCZ OBCY: Łączymy z id w tabeli users
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # RELACJA ODWROTNA: Dostęp do obiektu User z poziomu Konta
    owner: Mapped["User"] = relationship("User", back_populates="accounts")")
   
#  ------   [ transaction history bez zmian ]
```

Co tu się zmieniło względem Javy/SpringBoota?
---------------------------------------------
ForeignKey("users.id"): 
To jest ograniczenie na poziomie bazy danych (Constraint).

relationship(...): 
To jest mechanizm Pythona/SQLAlchemy. 
To nie tworzy kolumny w bazie, ale pozwala Ci napisać w kodzie:
`user.accounts`, a `SQLAlchemy` samo zrobi `JOIN` i dociągnie listę obiektów.

Mapped[list["Account"]]: 
To są podpowiedzi typów (Type Hints). 
Dzięki temu `PyCharm` podpowie Ci metody, gdy będziesz pracował na liście kont użytkownika.



Krok 4: Schematy Pydantic (schemas.py)
--------------------------------------
```python
class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
```

Krok 5: "Strażnik" w main.py
----------------------------
Teraz najważniejsza część. 
Tworzymy funkcję `get_current_user`, która będzie wstrzykiwana do każdego chronionego endpointu.

```python
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import verify_password, create_access_token, hash_password, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nie można zweryfikować uprawnień",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user
```

Krok 6: Endpointy Logowania i Chronione
---------------------------------------
Dodaj te trasy do main.py:

```python
# 1. Logowanie (Wymiana hasła na Token)
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Niepoprawny login lub hasło")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# 2. CHRONIONY ENDPOINT: Moje konta
@app.get("/accounts/me", response_model=list[AccountResponse])
async def get_my_accounts(current_user: User = Depends(get_current_user)):
    # Dzięki Depends(get_current_user) wiemy na 100%, że user jest zalogowany
    # i mamy dostęp do jego całego obiektu!
    return current_user.accounts
```

Krok 6: Dodaj endpoint `/register` w `main.py`:
-----------------------------------------------
Wklej to pod importami, obok innych tras. 
To pozwoli Ci stworzyć dowolnego użytkownika i od razu sprawdzić, czy zapisuje się w bazie.


```python
from schemas import UserCreate # upewnij się, że masz ten import!
from auth import hash_password

@app.post("/register", status_code=201)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. Sprawdzamy czy user już istnieje
    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Użytkownik już istnieje")
    
    # 2. Tworzymy nowego usera z hashowanym hasłem
    new_user = User(
        username=user_in.username,
        hashed_password=hash_password(user_in.password)
    )
    db.add(new_user)
    await db.commit()
    return {"message": "Użytkownik zarejestrowany pomyślnie"}
```

Dlaczego to jest "Enterprise"?

Zero haseł w RAM: 
Hasło idzie przez `Multipart Form` (standard OAuth2), jest weryfikowane Bcryptem i znika.

Stateless: 
Serwer nie trzyma sesji. 
Możesz mieć 100 kontenerów `FastAPI`, a każdy z nich obsłuży ten sam token `JWT` bez pytania centralnej bazy o sesję.

Dependency Injection: 
Zobacz na `current_user: User = Depends(get_current_user)`. 
To jest czysta elegancja. 
Jeśli chcesz, żeby endpoint był publiczny – usuwasz Depends. 
Jeśli chroniony – dodajesz.

Zadanie dla Ciebie:
-------------------
Zrób restart bazy bo dodaliśmy relację owner_id:
cd do folderu projektu MiniBank (`cd C:\dev\python-projects\PycharmProjects\PythonProject-2\MiniBank`)
1. Zatrzymaj wszystko: Ctrl+C.
2. Wyczyść wolumeny: `  docker-compose down -v  `
3. Uruchom ponownie: `  docker-compose up --build  `

Teraz jak teraz skutecznie zamknąć kłódkę?
Odśwież http://localhost:8000/docs.
Otwórz endpoint POST `/register` (nie potrzebuje kłódki).
Zarejestruj się: {"username": "jacek", "password": "test"}.
Teraz kliknij Authorize na górze strony.
Wpisz: username: `jacek` i  haslo: `test`.
Kliknij Authorize.
Teraz musi zadziałać. 
Kłódka się zamknie.
Gdy kłódka będzie zamknięta, spróbuj stworzyć konto bankowe przez `POST /accounts`. 
Zauważ jedną ważną zmianę: 
Twój kod teraz wymaga owner_id. 
Dzięki temu, że jesteś zalogowany, w następnym kroku nauczymy API, żeby samo brało Twoje ID z tokena, 
zamiast pytać o nie w JSON-ie.



Jeśli problem:
--------------
Sprawdź logi w terminalu PyCharma
Kiedy klikasz "Authorize" w Swaggerze i dostajesz błąd, spójrz na czarne okno terminala, gdzie działa Docker.
Jeśli widzisz tam SELECT ... FROM users WHERE username = 'admin' i potem nic, to znaczy, że usera nie ma w bazie.
Jeśli widzisz wielki czerwony błąd (Traceback), wklej go tutaj – pewnie brakuje jakiejś biblioteki (np. bcrypt lub cryptography).

 
Spróbuj w Swaggerze użyć przycisku "Authorize" (ikonka kłódki na górze). 
Swagger sam znajdzie Twój endpoint `/token` i pozwoli Ci się zalogować.

Po zalogowaniu spróbuj wejść na `/accounts/me`.
 


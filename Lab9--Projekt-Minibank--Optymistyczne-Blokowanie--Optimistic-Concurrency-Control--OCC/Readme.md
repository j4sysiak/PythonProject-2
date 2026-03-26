Lab9
----

Lab9--Projekt-Minibank--Optymistyczne-Blokowanie--Optimistic-Concurrency-Control--OCC
--------------------------------------------------------- ---------------------------

Wchodzimy w tryb High-Concurrency Finance.
Blokada pesymistyczna (FOR UPDATE) to "kłódka" na wierszu w bazie – jak jeden wątek czyta, drugi musi czekać.
Blokada optymistyczna (OCC) to zakład wiersza o wersję.
Jeśli podczas transakcji wiersz w bazie zmienił wersję (ktoś inny coś zapisał), Twój zapis się nie uda. 
To jest ultra-szybkie w systemach, gdzie rzadko zdarzają się konflikty, ale musimy mieć 100% pewność danych.
Zrobimy to w trzech krokach: Model, Logika, Test.

Skoro masz już testy (Twoja siatka bezpieczeństwa świeci się na zielono), możemy "rozpruć" główny silnik bazy danych bez strachu.
Dlaczego to robimy? (Teoria Architekta)
Twoja obecna blokada pesymistyczna (`.with_for_update()`) działa świetnie, ale ma jedną wadę: 
  - zabija wydajność przy gigantycznym ruchu
  - blokuje wiersze w bazie na czas całej transakcji (odczyt -> API Walut -> obliczenia -> zapis) więc inne przelewy muszą czekać w kolejce

Blokada Optymistyczna zakłada, że konflikty są rzadkie.
Odczytujemy dane (wersja = 1).
Sprawdzamy kursy walut i liczymy wszystko w pamięci RAM (baza nie jest zablokowana, inni mogą czytać!).
Przy zapisie (COMMIT) wysyłamy komendę: "Zmień saldo na X, ALE TYLKO JEŚLI wersja w bazie to nadal 1".
Jeśli w międzyczasie ktoś inny zdążył zmienić saldo (wersja w bazie to już 2), baza odrzuci nasz zapis, 
a SQLAlchemy rzuci błąd `StaleDataError`.
W Springu robi się to adnotacją `@Version`. 
W Pythonie to kwestia dodania jednego słownika do modelu.


Krok 1: Włączenie @Version w bazie (models.py)
----------------------------------------------
Pamiętasz, że w Labie 2 zapobiegawczo dodaliśmy już kolumnę `version` do klasy Account? 
Teraz musimy powiedzieć SQLAlchemy, żeby faktycznie zaczęło jej używać jako mechanizmu blokad.

Otwórz `models.py` i dodaj zmienną `__mapper_args__` na samym dole klasy Account:

```python
# models.py
# (upewnij się, że masz zaimportowany Integer)

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_name: Mapped[str] = mapped_column(String(100), nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")

    # Pole do blokad optymistycznych (@Version ze Springa)
    version: Mapped[int] = mapped_column(Integer, default=1)

    # --- TO JEST ODPOWIEDNIK @Version ze Springa ---
    __mapper_args__ = {
        "version_id_col": version # SQLAlchemy będzie pilnować tego pola!
    }
```

Dzięki temu `SQLAlchemy` samo będzie podbijać kolumnę version (+1) przy każdym UPDATE 
i automatycznie sprawdzać konflikty.

Krok 2: Usunięcie pesymistycznej blokady i obsługa konfliktów (main.py)
-----------------------------------------------------------------------
Teraz przebudujemy endpointy:
  1. przelewu (`/convert-transfer`)
  2. transferu (`/transfer`) 
  3. transaction (`/transaction`)


Wywalamy `.with_for_update()`, żeby nie blokować bazy.
Teraz bazujemy na tym, że jeśli wersja się nie zgadza przy commit(), `SQLAlchemy` automatycznie rzuci `StaleDataError`.
Dodajemy obsługę błędu `StaleDataError`, zwracając status 409 Conflict (Standard REST, 
gdy dwa systemy próbują edytować ten sam zasób).

Otwórz `main.py`, zmodyfikuj endpointy 
pod kątem usunięcia `.with_for_update()` i dodania obsługi `StaleDataError`:
 - `/transfer`
 - `/transaction`
 - `/convert-transfer`


```python
# Dodaj w sekcji importów na górze main.py:
from sqlalchemy.orm.exc import StaleDataError

# ... (zmodyfikowane wszystkie Endpointy finansowe: transfer, transaction and convert-transfer) ...
```


Krok 3: Udowodnienie, że to działa (Test Obciążeniowy)
------------------------------------------------------
Zapisz pliki (Docker się zrestartuje).
Wyzeruj stan: 
ustaw sobie w Swaggerze na Koncie A 100 PLN.


## Testing Optimistic Locking

W repo znajdują się dwa skrypty do testowania zachowania Optimistic Locking dla operacji przelewu (`/transfer`):

- `MiniBank/tests/load_test_optimistic.py` — wariant "remote": wysyła równoległe żądania HTTP do uruchomionego serwera (używa `requests`). Używaj go tylko jeśli serwer jest uruchomiony i masz pewność, że docelowa baza to środowisko testowe lub chcesz świadomie sprawdzić zachowanie w środowisku produkcyjnym.

- `MiniBank/tests/load_test_optimistic_local.py` — bezpieczny wariant lokalny: uruchamia aplikację in-process (ASGI) i przed importem wymusza `DATABASE_URL` wskazujący na lokalny plik `test_minibank.db` (SQLite). Używaj tego skryptu do testów lokalnych, aby nie zapisywać danych do produkcyjnej bazy Postgres.

Główne cele obu skryptów:
- symulować dużą liczbę równoległych przelewów pomiędzy dwoma kontami,
- zliczać odpowiedzi (200 success, 409 conflict — OCC, 400 bad request itp.),
- pobrać końcowe salda kont i porównać z liczbą udanych przelewów.

Jak uruchomić (lokalny, bezpieczny wariant)
1. Przejdź do katalogu projektu i aktywuj virtualenv:

```powershell
Set-Location C:\dev\python-projects\PycharmProjects\PythonProject-2
.\.venv\Scripts\Activate.ps1
```

2. Uruchom lokalny test (in-process, zapisuje do `test_minibank.db`):

```powershell
.\.venv\Scripts\python -m MiniBank.tests.load_test_optimistic_local
```

Skrypt wypisze statystyki: ile żądań zakończyło się statusem 200, ile 409 itp. Na końcu pokaże finalne salda kont — sprawdź, czy różnica sald odpowiada sumie pomyślnych transferów.

Jak uruchomić (remote / zdalny serwer)
1. Upewnij się, że aplikacja jest uruchomiona i że jej `DATABASE_URL` wskazuje środowisko, na którym chcesz testować (UWAGA: może to być produkcyjna baza!).
2. Uruchom:

```powershell
.\.venv\Scripts\python -m MiniBank.tests.load_test_optimistic
```

Możesz też ustawić adres serwera przez zmienną środowiskową `BASE_URL` przed uruchomieniem:

```powershell
$env:BASE_URL='http://localhost:8000'
.\.venv\Scripts\python -m MiniBank.tests.load_test_optimistic
```

Interpretacja wyników
- `Status 200` — przelew powiódł się i został zapisany.
- `Status 409` — konflikt optimistic locking (wersja w DB zmieniła się przed zapisem) — oczekiwane przy dużej konkurencji.
- `Status 400` — np. niewystarczające środki.

Przykład: jeśli uruchomisz 50 równoległych przelewów po 10.00 i otrzymasz 47 sukcesów (200) i 3 konflikty (409), to końcowa różnica sald powinna wynieść 47 * 10 = 470.

Wskazówki tuningowe
- Jeśli chcesz więcej sukcesów przy dużej konkurencji, zwiększ liczbę retryów (`RETRY_ON_CONFLICT`) i dodaj wykładniczy backoff z jitterem.
- Zmniejszenie liczby równoległych wątków/spawnowanych żądań zmniejszy liczbę konfliktów.
- Testy lokalne: używaj `load_test_optimistic_local.py` by uniknąć przypadkowych zapisów do środowiska produkcyjnego.

Sprawdzanie pliku testowej bazy (po uruchomieniu lokalnego testu)
```powershell
.\.venv\Scripts\python MiniBank/tests/test_if_test_inserted_data_to_db_on_SQLite.py
```
Albo uruchom snippet poniżej aby szybko zobaczyć tabele i kilka wierszy:

```python
import sqlite3
db = r"C:\dev\python-projects\PycharmProjects\PythonProject-2\test_minibank.db"
conn = sqlite3.connect(db)
print(conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
print(conn.execute("SELECT id, owner_name, balance FROM accounts").fetchall())
print(conn.execute("SELECT id, from_account_id, to_account_id, amount FROM transactions").fetchall()[:10])
conn.close()
```

Bezpieczeństwo
- Nigdy nie uruchamiaj `load_test_optimistic.py` przeciwko produkcyjnej bazy bez wcześniejszej zgody i bez świadomości konsekwencji — skrypt może tworzyć dużo rekordów.
- Zawsze preferuj `load_test_optimistic_local.py` do szybkich walidacji i CI.


## Przywracanie środowiska produkcyjnego (`DATABASE_URL`)

Jeżeli tymczasowo usunąłeś zmienną środowiskową `DATABASE_URL` przed uruchomieniem testów, możesz ją przywrócić do wartości produkcyjnej. 
Poniżej przykładowe polecenia dla PowerShell i Bash (zamień `user`, `pass`, `db` i `minibank` na swoje wartości):

PowerShell (tymczasowo w bieżącej sesji):


```powershell
Set-Item Env:\DATABASE_URL "postgresql+asyncpg://user:pass@db:5432/minibank"
```

PowerShell (trwale dla użytkownika) — przykład (PowerShell Core/Windows):

Uruchom to tylko jeśli chcesz zapisać URL na stałe (zamień user, pass, db, minibank).
To polecenie ustawia zmienną środowiskową DATABASE_URL trwale dla bieżącego użytkownika w PowerShell 
— używaj, jeśli chcesz, żeby Twoja aplikacja zawsze widziała ten URL po restarcie systemu.
```powershell
#[Environment]::SetEnvironmentVariable can be used to persist env variables for the current user
[Environment]::SetEnvironmentVariable('DATABASE_URL','postgresql+asyncpg://user:pass@db:5432/minibank','User')
```

Bash / macOS / Linux (tymczasowo w sesji):
Jeśli potrzebujesz tylko tymczasowo w bieżącej sesji, użyj:
```bash
export DATABASE_URL="postgresql+asyncpg://bank_admin:superhaslo123@db:5433/minibank"
```

Uwaga: ustawienie `DATABASE_URL` w systemie może wpłynąć na inne narzędzia i skrypty. 
Zadbaj o to, aby wartość była bezpieczna i nie trafiała do nieautoryzowanych kopii zapasowych ani logów.

## Uruchomienie aplikacji do developmentu z Docker Compose

W projekcie aplikacja produkcyjna zwykle korzysta z Postgresa uruchomionego w Dockerze. 
Poniżej przykładowe kroki jak uruchomić środowisko developerskie z Docker Compose i jak uruchomić aplikację lokalnie tak, 
by łączyła się z kontenerem DB.

1. Uruchom kontener bazy danych (zakładając, że masz `docker-compose.yml` z usługą `db`):

cd C:\dev\python-projects\PycharmProjects\PythonProject-2\MiniBank
```bash
# uruchom usługi w tle
docker compose up -d db
```

2. Ustaw `DATABASE_URL` wskazujący na kontener (przykład dla sieci Docker Compose):

PowerShell (tymczasowo):

```powershell
Set-Item Env:\DATABASE_URL "postgresql+asyncpg://bank_admin:superhaslo123@localhost:5433/minibank"
```

Uwaga: jeżeli aplikacja uruchomiona jest również jako kontener w tej samej sieci, 
jej `DATABASE_URL` może używać hosta `db` zamiast `localhost`.

3. Uruchom aplikację lokalnie (uvicorn) lub jako kontener:

Lokalnie (używając uvicorn):

cd C:\dev\python-projects\PycharmProjects\PythonProject-2
```bash
# z katalogu projektu, w aktywowanym virtualenv
uvicorn MiniBank.main:app --reload --host 0.0.0.0 --port 8000
```

Jako kontener (jeśli masz service `app` w compose):

```bash
docker compose up --build app
```

4. Sprawdź logi i połączenie:

```bash
docker compose logs -f db
curl http://localhost:8000/health
```

Jeżeli aplikacja nie łączy się z bazą, sprawdź:
- wartość `DATABASE_URL` (czy wskazuje na poprawny host/port/credencji),
- czy kontener DB jest w stanie `healthy` i nasłuchuje na porcie,
- czy firewall/porty są otwarte, jeśli łączysz się spoza Docker hosta.

---

Jeśli chcesz, mogę dodać przykład minimalnego `docker-compose.yml` dla Postgres + app, albo dodać instrukcję jak używać migracji (Alembic) w tym projekcie.
 


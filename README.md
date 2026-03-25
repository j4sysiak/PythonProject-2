# MiniBank - instrukcje uruchamiania testów

Ten plik zawiera instrukcje jak bezpiecznie uruchamiać testy lokalne w projekcie MiniBank.

## Uruchamianie testów lokalnych (Windows PowerShell)

Testy integracyjne w katalogu `MiniBank/tests/` używają lokalnej bazy SQLite `test_minibank.db`. Aby uruchomić pojedynczy plik testowy bez ryzyka łączenia się z produkcyjną bazą Postgres (np. uruchomioną w Dockerze), uruchom w PowerShell:

```powershell
Set-Location C:\dev\python-projects\PycharmProjects\PythonProject-2
# Usuń zmienną środowiskową DATABASE_URL (jeśli była ustawiona) - zapobiega użyciu produkcyjnej bazy
Remove-Item Env:\DATABASE_URL -ErrorAction SilentlyContinue
# Uruchom pytest dla pliku testowego
pytest MiniBank/tests/test_api.py -q
```

### Kroki bezpiecznego przygotowania
1. Aktywuj virtualenv:

```powershell
.venv\Scripts\Activate.ps1
```

2. (Opcjonalnie) Zresetuj schemę testowej bazy (drop + create):

```powershell
python -m MiniBank.scripts.reset_db --url "sqlite+aiosqlite:///./test_minibank.db" --yes
```

3. Uruchom testy (jak powyżej).

### Uwaga
- `Remove-Item Env:\DATABASE_URL` wpływa tylko na bieżącą sesję PowerShell. Jeśli `DATABASE_URL` jest ustawione trwale w systemie, usuń lub zmień je globalnie ostrożnie.
- Jeśli widzisz, że testy próbują łączyć się z `postgresql+asyncpg://...@db:5432/...`, upewnij się, że w sesji przed importami nie istnieje `DATABASE_URL` lub podaj jawnie `--url` w skrypcie resetu.
- Możesz uruchomić wszystkie testy poleceniem:

```powershell
pytest -v
```

## Reset DB

Aby zresetować (DROP + CREATE) schemę w pliku `test_minibank.db` użyj:

```powershell
python -m MiniBank.scripts.reset_db --url "sqlite+aiosqlite:///./test_minibank.db" --yes
```

- Skrypt wykona DROP wszystkich tabel i ponowne ich utworzenie. Upewnij się, że wskazujesz właściwy URL testowej bazy, aby nie usunąć danych produkcyjnych.

## Debug tips

- Sprawdź aktualną wartość `DATABASE_URL` w PowerShell:

```powershell
echo $env:DATABASE_URL
```

- Jeśli chcesz upewnić się, że import `MiniBank.database` korzysta z SQLite, uruchom:

```powershell
python -c "import os, importlib; os.environ['DATABASE_URL']='sqlite+aiosqlite:///./test_minibank.db'; db=importlib.import_module('MiniBank.database'); print(db.DATABASE_URL)"
```

- Jeśli napotkasz błędy C-level typu "Windows fatal exception: access violation" podczas uruchamiania testów:
  - Zaktualizuj zależności: `pip install -U anyio httpx starlette pytest pytest-asyncio`
  - Spróbuj uruchomić testy na innej wersji Pythona (np. 3.11/3.12) jeśli używasz 3.14.
  - Uruchamiaj pojedyncze testy żeby zlokalizować który teardown powoduje problem.

---


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

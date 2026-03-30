# Ręczne uruchomienie testów z pliku: test_api.py
# wymusza użycie SQLite test_minibank.db (jeśli DATABASE_URL nie jest ustawione)

1.
cd C:\dev\python-projects\PycharmProjects\PythonProject-2

2.
Set-Location C:\dev\python-projects\PycharmProjects\PythonProject-2

3.
. .\.venv\Scripts\Activate.ps1

4.
echo $env:DATABASE_URL

5.
jak bedzie ustawienie na postgresa `postgresql+asyncpg://user:pass@db:5432/miniban` to przelącz się na SQLite:

6.
$env:DATABASE_URL='sqlite+aiosqlite:///C:/dev/python-projects/PycharmProjects/PythonProject-2/test_minibank.db'

7.
echo $env:DATABASE_URL

powinno być: 
------------
`sqlite+aiosqlite:///C:/dev/python-projects/PycharmProjects/PythonProject-2/test_minibank.db`
  

8.              
uruchamiamy testy:
------------------
.\.venv\Scripts\python -m pytest MiniBank/tests/test_api.py::test_create_account -q -s
.\.venv\Scripts\python -m pytest MiniBank/tests/test_api.py::test_transfer_money_successfull -q -s
.\.venv\Scripts\python -m pytest MiniBank/tests/test_api.py::test_transfer_insufficient_funds -q -s
.\.venv\Scripts\python -m pytest MiniBank/tests/test_api.py::test_transaction_adding_money_successfull -q -s
.\.venv\Scripts\python -m pytest MiniBank/tests/test_api.py::test_transaction_withdrowal_money_successfull -q -s
.\.venv\Scripts\python -m pytest MiniBank/tests/test_api.py::test_convert_money_successfull -q -s


9.
sprawdzamy SQLite:
------------------
sprawdzamy w kliencie bazy (SQLite) czy konto zostało utworzone i czy transakcja została zarejestrowana (SELECT * FROM accounts; SELECT * FROM transactions;).


lub

# 4. Sprawdź zawartość pliku DB SQLite (np. `C:\dev\python-projects\PycharmProjects\PythonProject-2\test_minibank.db`) za pomocą klienta SQLite (np. DB Browser for SQLite) lub za pomocą polecenia sqlite3 w terminalu:
.\.venv\Scripts\python MiniBank/tests/test_if_test_inserted_data_to_db_on_SQLite.py

# Po tych krokach powinieneś zobaczyć tabele i wiersze.



# Testy: Optimistic Locking:
# Uwaga zapisuje na bazie produkcyjnej Postgresa
# ==========================    test:   load_test_optimistic.py    ==========================

Skrypt do testowania Optimistic Locking dla endpointu /transfer.

Co robi:
- tworzy dwa konta testowe via POST /accounts (jeśli istnieją, tworzy nowe)
- uruchamia N równoległych przelewów z konta A do B
- zlicza odpowiedzi: 200 (success), 409 (conflict - OCC), 400 (bad request / insufficient funds) i inne
- po przebiegu pobiera salda kont i wypisuje raport

Uruchomienie:
  - Upewnij się, że aplikacja działa na http://localhost:8000 lub ustaw env BASE_URL
  - python MiniBank/tests/load_test_optimistic.py

Uwaga: skrypt używa modułu `requests`. Jeśli nie masz go w venv, zainstaluj: pip install requests

# URUCHOMIENIE:
# Set-Location C:\dev\python-projects\PycharmProjects\PythonProject-2
# .\.venv\Scripts\Activate.ps1
# .\.venv\Scripts\python -m MiniBank.tests.load_test_optimistic_local


# Testy: Optimistic Locking:
# Uwaga zapisuje na bazie testowej SQLite
# ==========================    test:   load_test_optimistic_local.py    ==========================

Skrypt do testowania Optimistic Locking dla endpointu /transfer.
Wersja lokalna testu Optimistic Locking: uruchamia ASGI app w-process
i używa httpx.AsyncClient aby dokonywać wielu równoległych żądań bez sieci.

Ten skrypt USTAWIA przed importem aplikacji zmienną środowiskową
DATABASE_URL na lokalny plik SQLite (test_minibank.db) — dzięki temu
wszystkie zapisy trafią do pliku testowego, nie do produkcyjnego Postgresa.

# URUCHOMIENIE:
# Set-Location C:\dev\python-projects\PycharmProjects\PythonProject-2
# .\.venv\Scripts\Activate.ps1
# python -m MiniBank.tests.load_test_optimistic


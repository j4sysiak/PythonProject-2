# wymusza użycie SQLite test_minibank.db (jeśli DATABASE_URL nie jest ustawione)

cd C:\dev\python-projects\PycharmProjects\PythonProject-2
Set-Location C:\dev\python-projects\PycharmProjects\PythonProject-2

. .\.venv\Scripts\Activate.ps1

echo $env:DATABASE_URL

jak bedzie ustawienie na postgresa to przelącz się na SQLite:

$env:DATABASE_URL='sqlite+aiosqlite:///C:/dev/python-projects/PycharmProjects/PythonProject-2/test_minibank.db'

echo $env:DATABASE_URL

powinno być: 
------------
`sqlite+aiosqlite:///C:/dev/python-projects/PycharmProjects/PythonProject-2/test_minibank.db`
                
uruchamiamy testy:
------------------
.\.venv\Scripts\python -m pytest MiniBank/tests/test_api.py::test_create_account -q -s
.\.venv\Scripts\python -m pytest MiniBank/tests/test_api.py::test_transfer_insufficient_funds -q -s
tego jeszcze niema:   .\.venv\Scripts\python -m pytest MiniBank/tests/test_api.py::test_transfer_success -q -s

sprawdzamy SQLite:
------------------
sprawdzamy w kliencie bazy (SQLite) czy konto zostało utworzone i czy transakcja została zarejestrowana (SELECT * FROM accounts; SELECT * FROM transactions;).


lub

# 4. Sprawdź zawartość pliku DB SQLite (np. `C:\dev\python-projects\PycharmProjects\PythonProject-2\test_minibank.db`) za pomocą klienta SQLite (np. DB Browser for SQLite) lub za pomocą polecenia sqlite3 w terminalu:
.\.venv\Scripts\python MiniBank/tests/test_if_test_inserted_data_to_db_on_SQLite.py

# Po tych krokach powinieneś zobaczyć tabele i wiersze.
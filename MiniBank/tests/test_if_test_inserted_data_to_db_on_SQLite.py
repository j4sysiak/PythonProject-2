# UWAGA!
# ten test test odpalaj tylko z cmd:

# 1. Przejdź do katalogu głównego projektu (gdzie pakiet MiniBank jest widoczny):
#    Set-Location C:\dev\python-projects\PycharmProjects\PythonProject-2

# 2. Ustaw zmienną środowiskową (tylko na czas tej sesji PowerShell) tak, aby testy korzystały z pliku SQLite:
#    $env:DATABASE_URL = 'sqlite+aiosqlite:///C:/dev/python-projects/PycharmProjects/PythonProject-2/test_minibank.db'

# 3. Uruchom pojedynczy test (przykład - uruchomienie test_create_account):
#    .\.venv\Scripts\python -m pytest MiniBank/tests/test_api.py::test_create_account -q -s

# 4. Sprawdź zawartość pliku DB (te wlasnie skrypt):
#    .\.venv\Scripts\python MiniBank/tests/test_if_test_inserted_data_to_db_on_SQLite.py

# Po tych krokach powinieneś zobaczyć tabele i wiersze.


import sqlite3
db = r"C:\dev\python-projects\PycharmProjects\PythonProject-2\test_minibank.db"
conn = sqlite3.connect(db)
cur = conn.cursor()
print("Tables:", conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
try:
    print("Accounts rows:", conn.execute("SELECT id, owner_name, balance, currency, version FROM accounts").fetchall())
except Exception as e:
    print("SELECT error:", e)
cur.close()
conn.close()

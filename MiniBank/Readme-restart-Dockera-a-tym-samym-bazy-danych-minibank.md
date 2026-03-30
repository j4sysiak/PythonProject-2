Opcja Nuklearna (Restart Bazy)
------------------------------
cd do folderu projektu MiniBank (`cd C:\dev\python-projects\PycharmProjects\PythonProject-2\MiniBank`) 

W terminalu wciśnij Ctrl+C.
```log
Gracefully Stopping... press Ctrl+C again to force
 Container minibank_api  Stopping
 Container minibank_api  Stopped
 Container minibank_db  Stopping
 Container minibank_db  Stopped
```
Wpisz: docker-compose down -v
```log
time="2026-03-20T09:48:36+01:00" level=warning msg="C:\\dev\\python-projects\\PycharmProjects\\PythonProject-2\\MiniBank\\docker-compose.yml: the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion"
[+] Running 4/4
 ✔ Container minibank_api    Removed0.1s 
 ✔ Container minibank_db     Removed0.0s 
 ✔ Network minibank_default  Removed0.4s  
 ✔ Volume minibank_pgdata    Removed0.1s  
```
Wpisz: docker-compose build --no-cache api
Odpal> docker-compose up

```log
[+] Building 0.0s (0/0) 
[+] Running 2/2 
 ✔ Container minibank_db  Started 0.3s 
 ✔ Container minibank_api Started 0.4s 
```


baza Postgres zostanie zrestartowana, a wszystkie dane w niej zostaną usunięte (w tym konta i transakcje).
Jeśli chcesz zachować dane, możesz pominąć krok `docker-compose down -v` 
i po prostu uruchomić `docker-compose build --no-cache api` i odpal: `docker-compose up`, 
ale wtedy nie będzie efektu "restartu" bazy, a jedynie ponowne zbudowanie obrazu API.

1. Odpalamy klienta (Swagger) i sprawdzamy, że baza jest pusta (nie ma kont, transakcji itp.): http://localhost:8000/docs

2. Odpalamy klienta bazy (PostgreSQL lub SQLite) i sprawdzamy, że tabela `accounts` jest pusta (SELECT * FROM accounts;).
   plik bazy danych dla SQLite znajduje się w folderze projektu (np. `C:\dev\python-projects\PycharmProjects\PythonProject-2\MiniBank\minibank.db`).

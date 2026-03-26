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
Wpisz: docker-compose up --build
```log
[+] Building 0.0s (0/0) 
[+] Running 2/2
 ✔ minibank-api              Built                                                                                                                                            0.0s 
 ✔ Network minibank_default  Created                                                                                                                                          0.1s 
 ✔ Volume minibank_pgdata    Created                                                                                                                                          0.0s 
 ✔ Container minibank_db     Created                                                                                                                                          0.4s 
 ✔ Container minibank_api    Created      
    [ ... ]
minibank_api  | 2026-03-26 08:54:24,538 INFO sqlalchemy.engine.Engine [generated in 0.00071s] (0, 'SYSTEM', 999999.0, 'PLN', 1)
minibank_api  | 2026-03-26 08:54:24,543 INFO sqlalchemy.engine.Engine COMMIT
minibank_api  | INFO:     Application startup complete.
minibank_api  | INFO:     172.18.0.1:49982 - "GET /docs HTTP/1.1" 200 OK
minibank_api  | INFO:     172.18.0.1:49982 - "GET /openapi.json HTTP/1.1" 200 OK
(v) View in Docker Desktop       (o) View Config       (w) Enable Watch
```

Mozesz sprawdzic teraz, czy dziala baza Postgresa (to jest produkcja) tam w tabeli Account powinien byc tylko jeden rekord z kontem admina, a nie powinno byc zadnych rekordow z kontami testowymi. 
Sprawdzisz to w pgAdminie lub DBViewer, logujac sie do bazy danych Postgres (host: localhost, port: 5433, username: bank_admin, password: superhaslo123, database: minibank) i otwierajac tabele Account w bazie danych minibank_db.
i czy API (on Swagger) jest dostepne pod adresem http://localhost:8000/docs
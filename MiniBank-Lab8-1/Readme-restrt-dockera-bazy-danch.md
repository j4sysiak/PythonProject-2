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
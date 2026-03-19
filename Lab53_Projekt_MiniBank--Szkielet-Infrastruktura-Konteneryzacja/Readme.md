Lab53_Projekt_MiniBank--Szkielet-Infrastruktura-Konteneryzacja
--------------------------------------------------------------

Zapomnij o `Flasku` i `SQLite`. 
Użyjemy `FastAPI` (najszybszy obecnie framework w Pythonie, w pełni asynchroniczny) oraz `PostgreSQL`. 
Całość od razu pakujemy w Dockera.

W `FastAPI` nie musisz pisać DTOs (Data Transfer Objects) ręcznie ani konfigurować Swaggera. 
Framework sam waliduje typy danych i generuje dokumentację na podstawie typowania (Type `Hints`). 
Zobaczysz, jak bardzo skraca to kod w porównaniu do Javy.

Krok 1: Struktura katalogów
---------------------------
Utwórz nowy, pusty folder na dysku, np. MiniBank. Otwórz go w PyCharmie (lub VS Code).
Stworzymy w nim 4 pliki.

Krok 2: Zależności (requirements.txt) - plik-1/4
------------------------------------------------
To odpowiednik Twojego `pom.xml` z Mavena lub `build.gradle`. 
Definiujemy tu paczki.
Utwórz plik requirements.txt i wklej:

```text
fastapi==0.110.0
uvicorn[standard]==0.27.1
sqlalchemy==2.0.28
asyncpg==0.29.0
pydantic==2.6.4
```

(Uwaga: asyncpg to asynchroniczny sterownik do Postgresa, w Javie odpowiednik R2DBC/R2DBC-PostgreSQL).

Krok 3: Punkt wejścia aplikacji (main.py) - plik-2/4
----------------------------------------------------
To odpowiednik Twojej klasy z `@SpringBootApplication`. 
Uruchamia serwer i definiuje pierwszy endpoint (`Health Check`).
Utwórz plik main.py:

```python
from fastapi import FastAPI

# Inicjalizacja aplikacji
app = FastAPI(
    title="MiniBank API",
    description="System transakcyjny z blokadami optymistycznymi",
    version="1.0.0"
)

# Kontroler (odpowiednik @RestController i @GetMapping)
@app.get("/health")
async def health_check():
    return {"status": "UP", "message": "MiniBank serwer działa poprawnie"}
```

Krok 4: Konteneryzacja (Dockerfile) - plik-3/4
----------------------------------------------
Zapakujemy naszą aplikację w lekki obraz oparty na `Alpine Linux`.
Utwórz plik `Dockerfile` (bez rozszerzenia):

```yaml
# Oficjalny obraz Pythona
FROM python:3.11-slim

# Katalog roboczy w kontenerze
WORKDIR /app

# Kopiujemy plik z zależnościami i instalujemy je
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy resztę kodu
COPY . .

# Wystawiamy port (FastAPI domyślnie działa na 8000)
EXPOSE 8000

# Komenda startowa (odpowiednik java -jar). 
# Uvicorn to serwer ASGI (odpowiednik wbudowanego Tomcata/Netty)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

Krok 5: Orkiestracja środowiska (docker-compose.yml) - plik-4/4
---------------------------------------------------------------
Stawiamy obok siebie naszą aplikację API oraz bazę `PostgreSQL`.
Utwórz plik docker-compose.yml:

```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: minibank_api
    ports:
      - "8000:8000"
    volumes:
      - .:/app # Montujemy kod lokalny do kontenera, żeby działał hot-reload!
    environment:
      - DATABASE_URL=postgresql+asyncpg://bank_admin:superhaslo123@db:5432/minibank
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    container_name: minibank_db
    restart: always
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: bank_admin
      POSTGRES_PASSWORD: superhaslo123
      POSTGRES_DB: minibank
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

EGZEKUCJA (Uruchomienie systemu):
---------------------------------
Masz zainstalowanego Dockera na kompie, prawda?
Otwórz terminal w folderze projektu i wpisz komendę:

`docker-compose up --build`

Co się teraz dzieje?
--------------------
1. Docker pobiera obraz Postgresa i podnosi bazę na porcie 5432
2. Buduje obraz z Twoim kodem Pythona, instaluje paczki z requirements.txt
3. Odpala serwer Uvicorn (odpowiednik Wrapped Tomcat) na porcie 8000

Aplikacja dzięki volumes "widzi" Twoje lokalne pliki, 
            więc każda zmiana w kodzie natychmiast zrestartuje serwer wewnątrz kontenera (Hot Reload).

Test Inżyniera:
---------------
Kiedy logi w terminalu się uspokoją (zobaczysz Application startup complete):
Wejdź w przeglądarkę na Health Check: http://localhost:8000/health (Powinieneś dostać JSON-a z {"status":"UP"}).
A TERAZ NAJLEPSZE: Wejdź na http://localhost:8000/docs

Widzisz to?
`FastAPI` z automatu (bez ani jednej linijki konfiguracji) wygenerowało dla Ciebie pełnego, interaktywnego Swaggera (OpenAPI). 
Możesz stąd od razu testować swoje endpointy. 
W Javie musiałbyś rzeźbić z bibliotekami `springfox` albo `springdoc-openapi`.

Daj znać, jak podniesie się środowisko.
W Lab 2 zrobimy:
1. konfigurację asynchronicznego połączenia z bazą (SQLAlchemy)
2. stworzymy tabelę Account (Konta Bankowe)
3. użyjemy Pydantic do walidacji danych wejściowych


Dzień 44
--------

Day_44_SQLAlchemy
-----------------

Koniec z ulotnymi danymi. 
Teraz wszystko, co użytkownik wpisze w wyszukiwarkę, zostaje na twardym dysku w prawdziwej relacyjnej bazie danych (SQL).

Dlaczego SQLAlchemy? (Teoria Inżynierska)

Zamiast pisać surowe, brzydkie komendy w SQL (np. INSERT INTO tabela VALUES...), używamy tzw. ORM (Object-Relational Mapping).
SQLAlchemy to tłumacz. 
Ty piszesz zwykły, obiektowy kod w Pythonie (np. nowy_wpis = Historia(miasto="Berlin")), 
a SQLAlchemy samo w locie tłumaczy to na język SQL i gada z bazą danych. 
To standard w branży, bo jak kiedyś zmienisz bazę z małego SQLite na potężnego PostgreSQL, nie zmienisz w kodzie ani jednej linijki logiki.

Krok 1: Instalacja
------------------

Otwórz terminal w PyCharmie (upewnij się, że masz aktywne (.venv)) i wpisz:
`pip install flask-sqlalchemy`

Krok 2: Modyfikacja Backendu (main.py)
--------------------------------------

Podmień swój main.py na ten kod. 
(Pamiętaj o wklejeniu klucza API). 
Dodałem tu tworzenie bazy danych, definiowanie tabeli i zapisywanie każdego udanego wyszukiwania.

```python
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

app = Flask(__name__)
API_KEY = "TUTAJ_WKLEJ_SWOJ_KLUCZ_API"

# --- 1. KONFIGURACJA BAZY DANYCH ---
# Mówimy Flaskowi, że nasza baza to plik SQLite o nazwie 'weather_history.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather_history.db'
db = SQLAlchemy(app)

# --- 2. MODEL TABELI (Jak wygląda nasz arkusz w bazie) ---
class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Unikalny numer ID (Auto-inkrementacja)
    city = db.Column(db.String(100), nullable=False) # Nazwa miasta (max 100 znaków)
    temp = db.Column(db.Float, nullable=False) # Temperatura
    date = db.Column(db.String(100), nullable=False) # Data i godzina wyszukiwania

# Tworzenie pliku bazy danych (uruchomi się tylko raz, jeśli pliku jeszcze nie ma)
with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def home():
    # ZAWSZE pobieramy z bazy 5 ostatnich wyszukiwań (sortowane malejąco po ID)
    history = db.session.query(SearchHistory).order_by(SearchHistory.id.desc()).limit(5).all()

    if request.method == "POST":
        city = request.form.get("city_input")
        
        parameters = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }
        
        try:
            response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=parameters)
            response.raise_for_status()
            data = response.json()
            
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"].capitalize()
            official_city_name = data["name"]

            # --- 3. ZAPIS DO BAZY DANYCH ---
            # Tworzymy nowy "obiekt" w Pythonie
            new_search = SearchHistory(
                city=official_city_name,
                temp=temp,
                date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            # Dodajemy go do sesji i komitujemy (wysyłamy trwale do bazy)
            db.session.add(new_search)
            db.session.commit()
            
            # Odświeżamy zmienną history, żeby tabela na stronie zaktualizowała się od razu
            history = db.session.query(SearchHistory).order_by(SearchHistory.id.desc()).limit(5).all()

            return render_template("index.html", city_name=official_city_name, temperature=temp, weather_desc=description, history=history)

        except requests.exceptions.HTTPError:
            return render_template("index.html", error=f"Nie znaleziono miasta: {city}", history=history)
        except Exception as e:
            return render_template("index.html", error=f"Błąd serwera: {e}", history=history)

    return render_template("index.html", history=history)

if __name__ == "__main__":
    app.run(debug=True)
```

Krok 3: Modyfikacja Frontendu (templates/index.html)
----------------------------------------------------

W HTML-u musimy tylko dopisać na samym dole pętlę Jinja  `{% for %}`, 
która przeleci po zmiennej history i wygeneruje nam elegancką listę tekstową.

Podmień swój index.html na ten kod:

```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Dashboard Pogodowy</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 50px;">
    
    <h1 style="color: #333;">Wyszukiwarka Pogody</h1>
    
    <form action="/" method="POST" style="margin-bottom: 30px;">
        <input type="text" name="city_input" placeholder="Wpisz miasto..." required 
               style="padding: 10px; font-size: 16px; width: 200px;">
        <button type="submit" style="padding: 10px 20px; font-size: 16px; background-color: #0056b3; color: white; border: none; cursor: pointer;">Szukaj</button>
    </form>

    {% if city_name %}
    <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 300px;">
        <h2 style="color: #0056b3;">📍 {{ city_name }}</h2>
        <p style="font-size: 24px; margin: 5px 0;">🌡️ Temperatura: <strong>{{ temperature }} °C</strong></p>
        <p style="font-size: 18px; color: #666;">☁️ Warunki: {{ weather_desc }}</p>
    </div>
    {% endif %}

    {% if error %}
    <div style="color: red; margin-top: 20px;">
        <h3>Błąd: {{ error }}</h3>
    </div>
    {% endif %}

    <!-- NOWOŚĆ: HISTORIA Z BAZY DANYCH -->
    <div style="margin-top: 50px; background: white; padding: 20px; border-radius: 10px; width: 400px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h3 style="color: #333; border-bottom: 1px solid #ccc; padding-bottom: 10px;">Ostatnie wyszukiwania (SQL)</h3>
        <ul style="list-style-type: none; padding: 0;">
            <!-- Pętla for w Jinja przelatuje przez każdy obiekt z bazy -->
            {% for item in history %}
                <li style="padding: 5px 0; border-bottom: 1px dashed #eee;">
                    <strong>{{ item.city }}</strong>: {{ item.temp }} °C <span style="color: #999; font-size: 12px;">({{ item.date }})</span>
                </li>
            {% endfor %}
        </ul>
    </div>

</body>
</html>
```

Co się dzieje w tle (Inżynieria):
---------------------------------

`db.create_all()`: 
Gdy odpalasz ten skrypt po raz pierwszy, `Flask` zagląda do głównego folderu Twojego projektu 
(ściślej: do specjalnego folderu instance/, który sam stworzy). 
Szuka tam pliku `weather_history.db`. 
Jeśli go nie ma, tworzy nowiutką bazę danych z tabelą search_history.

`db.session.add / commit`: 
To transakcja. 
Najpierw dokładasz obiekt do wózka (add), a potem płacisz przy kasie (commit). 
Gdyby wystąpił błąd w trakcie, baza wycofałaby transakcję, żeby nie zapisać uszkodzonych danych. 
To fundament stabilności w SQL.

Zapytanie SELECT: 
Zamiast pisać `SELECT * FROM search_history ORDER BY id DESC LIMIT 5`, 
użyłeś Pythona: `db.session.query(SearchHistory).order_by(SearchHistory.id.desc()).limit(5).all()`. 
Mówiłem, że ORM to potęga.

Przetestuj to na twardo:
------------------------

Zrestartuj serwer w PyCharmie.

Wejdź na `127.0.0.1:5000`. 
Wyszukaj np. "Berlin". 
Pod spodem na liście pojawi się wpis z sekundą wyszukiwania.

Wyszukaj "Londyn". 
Pojawi się na górze listy.

Teraz ostateczny test: 
Ubij serwer całkowicie (czerwony kwadrat). 
Odpal go znowu i wejdź na stronę. 
Historia tam jest. 
Przetrwała wyłączenie programu, bo leży bezpiecznie na dysku w pliku .db.

Zrobiłeś to. 
Masz w 100% komercyjny stos technologiczny (Frontend HTML + Backend Python + Baza Danych SQL + Zewnętrzne API).

Daj znać, jak to śmiga! 
Co robimy dalej? (np. REST API – jak wystawić te dane w bazie jako JSON dla innych programistów? Dzień 66).



--------------------    client SQL    ---------------
-----------------------------------------------------
Chcę zobaczyć a bazę, tj odpalić klienta bazy danych.
-----------------------------------------------------

I to jest podejście prawdziwego inżyniera. 
Aplikacja aplikacją, ale na koniec dnia musisz umieć zajrzeć do "surowych" danych, żeby sprawdzić, czy kod Cię nie oszukuje.

Baza, którą właśnie stworzyliśmy, to SQLite. 
Jest to specjalny typ bazy danych, który nie wymaga stawiania wielkiego serwera w tle (jak MySQL czy PostgreSQL) 
                 – cała baza to po prostu jeden plik na Twoim dysku.

Skoro używasz `PyCharm Community Edition`, nie masz dostępu do wbudowanych narzędzi bazodanowych `JetBrains` (są tylko w płatnej wersji Pro). 
Ale to żaden problem, bo w branży i tak używa się do tego dedykowanych, darmowych klientów.

Oto jak to zrobić w 3 minuty:

Krok 1: Zlokalizuj plik bazy
----------------------------
W nowym `Flasku` plik bazy danych nie tworzy się luzem obok main.py. 
Flask ze względów bezpieczeństwa tworzy w Twoim projekcie ukryty folder o nazwie `instance`.
Rozwiń ten folder w drzewie plików w PyCharmie (po lewej stronie) – tam leży Twój plik weather_history.db.

`C:\dev\python-projects\PycharmProjects\PythonProject-2\Day_44_SQLAlchemy\instance\weather_history.db`


Krok 2: Pobierz darmowego klienta (Standard branżowy)
-----------------------------------------------------
Najlepszym, najlżejszym i najpopularniejszym programem do podglądu takich plików jest `DB Browser for SQLite`.

Wejdź na oficjalną stronę: `sqlitebrowser.org`

Pobierz wersję na Windowsa (najlepiej "Standard installer" dla 64-bit) i zainstaluj (zwykłe Dalej -> Dalej).

Krok 3: Otwórz bazę i zobacz tabele
-----------------------------------
Odpal program DB Browser for SQLite.
Na samej górze kliknij duży przycisk "Otwórz bazę danych" (Open Database).
Przeklikaj się na dysku do folderu ze swoim projektem -> wejdź w folder instance -> wybierz plik weather_history.db.

Program wczyta bazę.
W zakładce "Struktura bazy danych" (Database Structure) zobaczysz swoją tabelę search_history i jej kolumny (id, city, temp, date).

Kliknij drugą zakładkę: "Przeglądaj dane" (Browse Data).
BUM! Widzisz całą tabelę jak w Excelu. 
Widzisz wszystkie miasta, które wpisałeś w przeglądarce, dokładnie tak, jak zapisał je Twój kod w Pythonie.

Dlaczego to jest potężne?
-------------------------
W tym programie (zakładka "Wykonaj SQL / Execute SQL") możesz pisać surowe komendy bazodanowe.
Możesz wpisać:
`SELECT * FROM search_history WHERE temp > 15.0;`
Wcisnąć Play i baza zwróci Ci tylko te wyszukiwania, gdzie było cieplej niż 15 stopni.

To jest moment, w którym zamyka się pętla. 
Widzisz:
 - backend (Python)
 - frontend (HTML)
 - API (OpenWeather)
 - surowe dane (SQL).

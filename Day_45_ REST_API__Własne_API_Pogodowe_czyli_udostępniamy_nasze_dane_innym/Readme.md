Dzień 45
--------

Day_45_ REST_API__Własne_API_Pogodowe_czyli_udostępniamy_nasze_dane_innym
-------------------------------------------------------------------------

Budujemy REST API.
REST API - czyli jak sprawić, żeby Twój serwer nie zwracał HTML-a dla ludzi, tylko JSON-a dla innych programistów (lub dla mobilnych aplikacji).
 

Pamiętasz, jak w Dniu 32 odpytywałeś serwer OpenWeatherMap, żeby dostać JSON-a z pogodą? 
`data = response.json()` - to była ta część, gdzie "rozpakowywałeś" paczkę z internetu. 
Dzisiaj Ty stajesz się takim serwerem OpenWeatherMap. Wystawisz na zewnątrz bazę danych, którą przed chwilą zbudowaliśmy.

Teoria w 3 zdaniach (Inżynieria):
---------------------------------

REST (Representational State Transfer): 
To zbiór zasad. 
Najważniejsza to używanie odpowiednich metod HTTP do odpowiednich akcji: 
 - GET (czytaj)
 - POST (zapisz)
 - PATCH (edytuj)
 - DELETE (usuń)

JSON: 
Twój serwer nie zwraca już `render_template("index.html")`. 
Zwraca `jsonify(...)`, czyli czyste dane, które każdy inny język programowania na świecie potrafi przeczytać.

Postman: 
W pracy nikt nie testuje API przez zwykłą przeglądarkę, bo przeglądarka potrafi robić tylko żądania GET. 
Używa się do tego programu Postman (lub podobnych), ale na nasze potrzeby dzisiaj wystarczy przeglądarka i prosty kod.

Projekt: Własne API Pogodowe

Utwórz nowy projekt Day_66_REST_API.
Ważne: Skopiuj folder instance (z plikiem weather_history.db w środku) z poprzedniego projektu i wklej go do nowego projektu, żebyśmy mieli na czym pracować.

Wklej to do main.py:

```python
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather_history.db'
db = SQLAlchemy(app)

# 1. MODEL TABELI (Musimy go mieć, żeby Flask wiedział, jak czytać bazę)
class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    temp = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(100), nullable=False)

    # METODA POMOCNICZA: Zamienia obiekt z bazy (którego JSON nie rozumie) na zwykły słownik
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

# --- 2. ENDPOINT: GET (Zwraca całą historię) ---
@app.route("/api/history", methods=["GET"])
def get_all_history():
    records = db.session.query(SearchHistory).all()
    # Przelatujemy przez wszystkie rekordy, zamieniamy na słowniki i pakujemy w JSON
    return jsonify(history=[record.to_dict() for record in records])

# --- 3. ENDPOINT: GET z filtrowaniem po mieście (Query Parameters) ---
@app.route("/api/search", methods=["GET"])
def search_city():
    # Pobiera z paska adresu parametr ?city=...
    query_city = request.args.get("city")
    
    # Szukamy w bazie tylko tych wpisów, gdzie miasto się zgadza
    records = db.session.query(SearchHistory).filter_by(city=query_city).all()
    
    if records:
        # Zwracamy kod 200 (OK) - Flask robi to domyślnie
        return jsonify(results=[record.to_dict() for record in records])
    else:
        # Zwracamy kod 404 (Not Found), jeśli miasta nie było w bazie
        return jsonify(error={"Not Found": "Brak historii dla tego miasta."}), 404

# --- 4. ENDPOINT: DELETE (Usuwanie z bazy - Wymaga klucza!) ---
@app.route("/api/history/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):
    # Sprawdzamy, czy programista podał poprawny klucz w adresie ?api_key=...
    api_key = request.args.get("api_key")
    if api_key == "TajneHasloSzefa":
        record_to_delete = db.session.get(SearchHistory, record_id)
        if record_to_delete:
            db.session.delete(record_to_delete)
            db.session.commit()
            return jsonify(success={"Message": "Rekord usunięty pomyślnie."}), 200
        else:
            return jsonify(error={"Not Found": "Brak rekordu o takim ID."}), 404
    else:
        # Zwracamy kod 403 (Forbidden), gdy klucz jest zły
        return jsonify(error={"Forbidden": "Brak uprawnień. Zły klucz API."}), 403

if __name__ == "__main__":
    app.run(debug=True)
```

Co tu się dzieje pod maską (Inżynieria):

jsonify(): 
To jest odwrotność `response.json()`, którego używałeś w bocie. 
Tam "rozpakowywałeś" paczkę z internetu, tutaj ją "pakujesz" dla kogoś innego.

Metoda to_dict(self): 
Baza SQL zwraca dziwne obiekty. 
JSON potrafi czytać tylko listy i słowniki. 
Ta mała metoda (z użyciem Dictionary Comprehension z Dnia 26!) automatycznie czyta nazwy kolumn i robi z nich elegancki słownik.

Query Parameters (request.args.get): 
Zauważ różnicę w adresach. Zamiast `/<city>`, używamy `?city=Berlin`. 
To standard przy filtrowaniu danych w API.

Zabezpieczenia (Metoda DELETE): 
Nie chcesz, żeby byle kto wszedł do internetu i skasował Ci bazę. 
Sprawdzasz "Klucz API" (tutaj po prostu twarde hasło). 
Jeśli się nie zgadza, rzucasz w twarz błędem 403 Forbidden.

Jak to przetestować jak profesjonalista:

Odpal serwer.
-------------

1. Wejdź w przeglądarkę i wpisz: http://127.0.0.1:5000/api/history
   BUM! Widzisz surowego JSON-a, dokładnie takiego, jakiego daje Google czy OpenWeatherMap.

2. Wpisz: http://127.0.0.1:5000/api/search?city=Berlin
   Widzisz tylko historię dla Berlina.

3. Wpisz: http://127.0.0.1:5000/api/search?city=Nibylandia
   Dostajesz ładny, Twój własny błąd 404 w formacie JSON.

(Metody DELETE nie przetestujesz ze zwykłego paska adresu przeglądarki, bo przeglądarka umie tylko w GET. 
Do tego służy narzędzie Postman albo napisanie bota w osobnym pliku Pythona).



dodajemy obslugę POST i DELETE
------------------------------

Właśnie zderzyłeś się z największym ograniczeniem przeglądarek internetowych. 
Zwykły pasek adresu w Chrome potrafi robić TYLKO zapytania `GET` (czyli "daj mi dane").

Żeby przetestować `POST` (dodawanie do bazy) i `DELETE` (usuwanie z bazy), programiści używają aplikacji typu Postman. 
Ale my jesteśmy inżynierami – mamy przecież bibliotekę requests, za pomocą której przed chwilą pisaliśmy bota! 
Zamiast instalować kolejne programy, napiszemy drugi, mały skrypt w Pythonie, który będzie "klientem" naszego API.

Krok 1: Dodajemy obsługę POST do Twojego API (main.py)
------------------------------------------------------

Do pliku main.py musisz dodać import czasu na samej górze (jeśli go nie masz):

```python
from datetime import datetime
```

A na dole, pod endpointem search_city (a nad delete_record), wklej ten nowy endpoint do odbierania danych POST:

```python
# --- 5. ENDPOINT: POST (Dodawanie nowego rekordu przez API) ---
@app.route("/api/history", methods=["POST"])
def add_record():
    # Odbieramy dane wysłane w "ciele" zapytania (tzw. form-data)
    new_city = request.form.get("city")
    new_temp = request.form.get("temp")

    # Zabezpieczenie: jeśli ktoś wyśle POST, ale zapomni podać miasta lub temperatury
    if not new_city or not new_temp:
        # Kod 400 = Bad Request (Złe żądanie od klienta)
        return jsonify(error={"Bad Request": "Brak parametrów 'city' lub 'temp'."}), 400

    # Tworzymy nowy rekord i pchamy do bazy SQL
    new_record = SearchHistory(
        city=new_city,
        temp=float(new_temp),
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    db.session.add(new_record)
    db.session.commit()

    # Kod 201 = Created (Pomyślnie utworzono nowy zasób na serwerze)
    return jsonify(response={"Success": "Pomyślnie dodano nowy wpis do bazy."}), 201
```


Zapisz plik i upewnij się, że serwer Flask cały czas działa w tle. 
Zostawiamy go włączonego.

Krok 2: Tworzymy "Klienta" do testów (Nowy plik)
------------------------------------------------

Teraz zasymulujemy sytuację, w której jakaś inna aplikacja (np. z telefonu komórkowego) uderza do Twojego serwera, żeby dodać i usunąć dane.

W tym samym projekcie stwórz nowy, oddzielny plik i nazwij go `tester.py`. Wklej do niego to:

```python
import requests

BASE_URL = "http://127.0.0.1:5000"

print("--- TESTUJEMY POST (Dodawanie do bazy) ---")
# Pakujemy dane, które chcemy wysłać do serwera (jak wypełnianie formularza)
post_data = {
    "city": "Tokio",
    "temp": 22.5
}
# Wysyłamy zapytanie POST na adres naszego serwera
response_post = requests.post(url=f"{BASE_URL}/api/history", data=post_data)
print(f"Status CODE: {response_post.status_code}")
print(response_post.json())


print("\n--- TESTUJEMY DELETE (Usuwanie z bazy) ---")
# Chcemy usunąć rekord o ID = 1. Używamy klucza API, żeby serwer nas nie odrzucił.
record_id_to_delete = 1
api_key = "TajneHasloSzefa"

# Wysyłamy zapytanie DELETE
response_delete = requests.delete(url=f"{BASE_URL}/api/history/{record_id_to_delete}?api_key={api_key}")
print(f"Status CODE: {response_delete.status_code}")
print(response_delete.json())
```

Krok 3: Odpal testy (Po inżyniersku)
------------------------------------

Mając włączony serwer Flask w jednym terminalu:

Kliknij prawym przyciskiem myszy wewnątrz pliku tester.py i wybierz Run 'tester'.

W konsoli zobaczysz odpowiedź od swojego własnego serwera:

W teście POST dostaniesz status 201 i komunikat "Success".

W teście DELETE dostaniesz status 200 i komunikat "Success" (lub 404, jeśli wcześniej nie miałeś rekordu z ID=1).

Wejdź w przeglądarkę pod adres: http://127.0.0.1:5000/api/history
Zobaczysz, że "Tokio" z temperaturą 22.5 magicznie pojawiło się w bazie danych, a stary rekord nr 1 (np. Twój stary Berlin) zniknął bezpowrotnie.

Dlaczego to jest potężne?

Właśnie stworzyłeś Mikroserwis.
Twój Flask to teraz niezależny byt (Backend). Twój tester.py to "Frontend" (mógłby być napisany w Javie, JavaScriptcie albo C++). Rozmawiają ze sobą uniwersalnym językiem zapytań HTTP (GET, POST, DELETE) i wymieniają się danymi w JSON-ie.

Dokładnie tak działa 99% dzisiejszego internetu – od aplikacji bankowych po Netflixa.

Działa Ci ten tester? Serwer przyjął dane i usunął rekord?



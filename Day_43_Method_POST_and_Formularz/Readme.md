Dzień 43
--------

Day_43_Method_POST_and_Formularz
--------------------------------


Co dalej?
Zgodnie z kursem Angeli wchodzimy teraz w decydującą fazę aplikacji webowych. 
Masz 2 kroki, oba są krytyczne w prawdziwej pracy:

Krok-1: Formularze i metody POST (Day_43_Method_POST_and_Formularz)
-------------------------------------------------------------------
Najpierw interfejs dla człowieka.
Teraz, żeby sprawdzić pogodę, musisz ręcznie wpisywać /Berlin w pasku adresu przeglądarki. 
To dobre dla programistów, ale zwykły użytkownik tego nie ogarnie.

Co zrobimy: 
Dodamy na środku Twojej strony normalne pole tekstowe i przycisk "Szukaj". 
Nauczysz się różnicy między zapytaniem `GET` (daj mi stronę) a `POST` (wysyłam Ci dane z formularza).


Krok-2: Bazy Danych SQL (Day_44_SQLAlchemy)
-------------------------------------------
Pamiętasz, jak zapisywaliśmy hasła do pliku .txt albo .json? 
W aplikacjach webowych tego się NIE ROBI. 
Używa się baz danych.

Co zrobimy: 
Podepniemy pod Twojego Flaska prawdziwą, lokalną bazę danych SQLite. 
Będziesz mógł np. zapisywać w tabeli każde miasto, które ktoś wyszukał, i godzinę wyszukiwania.

Zaczynamy:
----------
Do tej pory używałeś tzw. zapytań GET – po prostu wpisywałeś adres, a serwer "dawał" Ci stronę. 
Teraz wprowadzamy zapytania `POST` – czyli Ty wpisujesz coś w formularzu na stronie, klikasz przycisk i wysyłasz te dane (pod maską) do serwera.

Teoria w 2 zdaniach (Inżynieria):
---------------------------------

Formularz HTML (<form>): 
Musi mieć metodę `POST` i każde pole tekstowe musi mieć atrybut: `name`. 
To po tym `name` Python rozpozna, co mu wysłałeś.

Obiekt request we Flasku: 
Służy do przechwytywania tego, co przyleciało z przeglądarki np: `request.form.get("nazwa_pola")`.

Zmieniamy nasz projekt. Zrobimy to jak profesjonaliści – na jednej stronie. Na górze wyszukiwarka, pod spodem wynik.

Krok 1: Aktualizacja Frontendu (templates/index.html)
-----------------------------------------------------

Podmień cały kod w pliku index.html na ten. 
Zwróć uwagę na blok <form> oraz instrukcję warunkową `Jinja` {% if city_name %} (wynik pokaże się tylko wtedy, gdy Python prześle miasto).

```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Dashboard Pogodowy</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 50px;">
    
    <h1 style="color: #333;">Wyszukiwarka Pogody</h1>
    
    <!-- 1. FORMULARZ (Wysyła dane metodą POST) -->
    <form action="/" method="POST" style="margin-bottom: 30px;">
        <!-- Atrybut 'name' jest kluczowy dla Pythona! -->
        <input type="text" name="city_input" placeholder="Wpisz miasto..." required 
               style="padding: 10px; font-size: 16px; width: 200px;">
        <button type="submit" style="padding: 10px 20px; font-size: 16px; background-color: #0056b3; color: white; border: none; cursor: pointer;">Szukaj</button>
    </form>

    <!-- 2. WARUNKOWE WYŚWIETLANIE (Jinja) -->
    <!-- Ten blok HTML wygeneruje się TYLKO jeśli Python przekaże zmienną 'city_name' -->
    {% if city_name %}
    <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 300px;">
        <h2 style="color: #0056b3;">📍 {{ city_name }}</h2>
        <p style="font-size: 24px; margin: 5px 0;">🌡️ Temperatura: <strong>{{ temperature }} °C</strong></p>
        <p style="font-size: 18px; color: #666;">☁️ Warunki: {{ weather_desc }}</p>
    </div>
    {% endif %}

    <!-- Obsługa błędów w HTML (jeśli Python prześle zmienną 'error') -->
    {% if error %}
    <div style="color: red; margin-top: 20px;">
        <h3>Błąd: {{ error }}</h3>
    </div>
    {% endif %}

</body>
</html>
```

Krok 2: Aktualizacja Backendu (main.py)
---------------------------------------

Podmień swój main.py.
Wklej swój klucz API.
Zwróć uwagę na to, że importujemy teraz request, a nasza główna trasa obsługuje obie metody: 
 - GET (kiedy wchodzisz na stronę)
 - POST (kiedy klikasz przycisk). 



```python
from flask import Flask, render_template, request
import requests

app = Flask(__name__)
API_KEY = "TUTAJ_WKLEJ_SWOJ_KLUCZ_API"

# Dodajemy obsługę metod GET i POST
@app.route("/", methods=["GET", "POST"])
def home():
    # 1. Jeśli użytkownik WCHODZI na stronę (GET), pokazujemy mu tylko pusty formularz
    if request.method == "GET":
        return render_template("index.html")

    # 2. Jeśli użytkownik KLIKNĄŁ przycisk (POST), przechwytujemy dane i odpytujemy API
    if request.method == "POST":
        # 'city_input' to dokładnie ten sam 'name', który wpisaliśmy w <input> w HTML!
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

            # Zwracamy ten sam szablon, ale tym razem Z DANYMI (więc Jinja pokaże kafelek)
            return render_template("index.html", city_name=official_city_name, temperature=temp, weather_desc=description)

        except requests.exceptions.HTTPError:
            # Jeśli API zwróci 404 (nie ma takiego miasta), przekazujemy błąd do HTML
            return render_template("index.html", error=f"Nie znaleziono miasta: {city}")
        except Exception as e:
            return render_template("index.html", error=f"Błąd serwera: {e}")

if __name__ == "__main__":
    app.run(debug=True)
```

Dlaczego to jest potężne (Pod maską):

`request.form.get("nazwa")`: 
To jest most między Frontend'em a Backend'em. 
żytkownik wpisuje dane w przeglądarce, przeglądarka pakuje je w ukrytą paczkę POST, a Twój kod we Flasku ją rozpakowuje.

Jeden adres URL (/): 
Zauważ, że nie robimy już tras typu `/Berlin`. 
Cała logika siedzi pod jednym głównym adresem. 
Kod sam decyduje, co zrobić, na podstawie tego, czy użytkownik tylko prosi o stronę (GET), czy też wysyła dane formularza (POST).

Instrukcje warunkowe w HTML ({% if %}):    `{% if city_name %} / {% endif %}`  i  `{% if error %} / {% endif %}`
To sprawia, że Twój interfejs jest dynamiczny. 
Kafelek z pogodą "nie istnieje" w kodzie HTML, dopóki Python nie przekaże mu danych z API.

Przetestuj to:
--------------

Zrób na wszelki wypadek twardy restart serwera (Czerwony kwadrat -> Play).
Wejdź na http://127.0.0.1:5000/. Zobaczysz tylko pole wyszukiwania.

Wpisz "Krakow" i wciśnij Szukaj.
Ułamek sekundy później strona się przeładuje i pod spodem wyskoczy piękny kafelek z temperaturą.

Wpisz "Bzdura123" – dostaniesz ładny, czerwony komunikat o błędzie na stronie, a nie w konsoli.

Działa? 
Jeśli tak, to wjechałeś w świat pełnoprawnych aplikacji webowych (tzw. Full-Stack).
Możesz przyjąć dane, przetworzyć je i oddać wynik na tej samej stronie.

Jak klikniesz i to ruszy, to zabieramy się za to, co odróżnia zabawki od systemów komercyjnych – Bazy Danych (SQLAlchemy). 
Będziemy logować każde miasto, które ktoś wpisał w wyszukiwarkę.




















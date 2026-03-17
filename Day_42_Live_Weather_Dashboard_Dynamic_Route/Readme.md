Dzień 42
--------

Day_42_Live_Weather_Dashboard_Dynamic_Route
-------------------------------------------

Wchodzimy w temat Dynamicznego Routingu. 
To jest ten moment, kiedy zdajesz sobie sprawę, dlaczego używamy render_template i szablonów Jinja.

Wyobraź sobie, że Twój szef chce sprawdzać pogodę dla 100 różnych miast, w których macie biura. 
W starym, głupim HTML-u musiałbyś stworzyć 100 plików (berlin.html, warszawa.html, londyn.html).
We Flasku robisz JEDNĄ trasę (route) i używasz tego samego, jednego pliku `index.html`, który już masz.

Jak to zrobić (Czysta Inżynieria):

Tym razem zmieniamy API. 
Zamiast szukać po twardych współrzędnych (lat, lon), każemy `OpenWeatherMap` szukać po nazwie miasta (parametr q).

Podmień swój plik main.py na ten kod. 
Twój plik templates/index.html zostaje w 100% BEZ ZMIAN!

```python
from flask import Flask, render_template
import requests

app = Flask(__name__)

API_KEY = "TUTAJ_WKLEJ_SWOJ_KLUCZ_API"

# 1. DYNAMICZNA TRASA: Znak < > mówi Flaskowi: "Cokolwiek user wpisze po ukośniku, 
# wrzuć to do zmiennej city_name i przekaż do funkcji".
@app.route("/<city_name>")
def get_weather(city_name):
    # 2. Zmieniamy parametry API. Zamiast lat/lon, używamy "q" (Query), czyli nazwy miasta.
    parameters = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=parameters)
        response.raise_for_status()
        data = response.json()
        
        # Wyciągamy dane dokładnie tak samo
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"].capitalize()
        # Bierzemy oficjalną nazwę miasta z API (żeby np. "londyn" zamieniło na ładne "London")
        official_city_name = data["name"]

        # 3. Zwracamy ten sam szablon, wstrzykując nowe dane
        return render_template("index.html", city_name=official_city_name, temperature=temp, weather_desc=description)

    # Co jeśli ktoś wpisze miasto, którego nie ma (np. /Nibylandia)? API zwróci błąd 404!
    except requests.exceptions.HTTPError:
        return f"<h1>Błąd 404</h1><p>Nie znaleziono miasta: <b>{city_name}</b>. Sprawdź literówkę w adresie.</p>"
    except Exception as e:
        return f"<h1>Błąd serwera</h1><p>{e}</p>"

if __name__ == "__main__":
    app.run(debug=True)
```

Co tu jest najważniejsze (Mechanika pod maską):

Zmienne w URL (<city_name>): 
Kiedy wpiszesz w przeglądarce 127.0.0.1:5000/Warszawa, Flask automatycznie łapie słowo "Warszawa", 
traktuje je jako zmienną `city_name` i przekazuje ją do funkcji `get_weather(city_name)`.

Skalowalność:
Właśnie napisałeś kod, który obsługuje dziesiątki tysięcy miast na całym świecie. 
Aplikacja nie urosła nawet o jedną linijkę HTML-a. 
To jest potęga backendu.

Obsługa błędów użytkownika (HTTPError): 
Użytkownicy robią literówki. 
Jak ktoś wpisze /Warszzzawa, `OpenWeatherMap` odrzuci to z błędem 404. 
Nasz blok except `requests.exceptions.HTTPError:` łapie ten konkretny błąd i zamiast wywalać serwer, 
wyświetla ładny komunikat, że miasto nie istnieje.

Przetestuj to na brutalnie:

Odpal serwer.
W przeglądarce wpisz: http://127.0.0.1:5000/Berlin
Potem zmień adres na: http://127.0.0.1:5000/Warszawa
Zmień na: http://127.0.0.1:5000/Tokyo
Na koniec wpisz: http://127.0.0.1:5000/KoziaWolka (żeby zobaczyć, jak elegancko obsługuje błąd).

Działa? Zmienia się miasto i temperatura? 
Jeśli tak, to w pełni zrozumiałeś, jak działają systemy typu Facebook, Wikipedia czy Allegro. 
Tam też jest jeden "szablon" profilu czy produktu, do którego Flask (lub inny framework) wstrzykuje dane na podstawie tego, 
co masz w pasku adresu przeglądarki.

Co robimy dalej? Jesteśmy gotowi na podpinanie pod to prawdziwej Bazy Danych (SQL), 
żeby np. zapisywać historię wyszukiwań?


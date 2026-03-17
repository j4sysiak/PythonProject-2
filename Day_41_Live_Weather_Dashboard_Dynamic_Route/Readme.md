Dzień 41
--------

Day_41_Live_Weather_Dashboard_Dynamic_Route
-------------------------------------------

Wchodzimy na poziom profesjonalny. 
Wrzucanie kodu HTML prosto do pliku Pythona (tak jak zrobiliśmy to przed chwilą w Day_40) to tzw. "hardcoding". 
W prawdziwej pracy za wygląd strony odpowiada Frontend Developer, a Ty jako Backend Developer masz mu tylko dostarczyć dane. 
Nie możecie grzebać w tym samym pliku.

Rozwiązaniem jest Szablonowanie (Templating) przy użyciu wbudowanego we `Flask` silnika `Jinja`.

Żelazna zasada Flaska: Struktura folderów

Flask jest bardzo rygorystyczny. 
Jeśli chcesz wczytywać pliki HTML, musisz stworzyć specjalny folder.

W głównym folderze swojego projektu (tam gdzie masz main.py) utwórz nowy folder i nazwij go dokładnie tak: 
`templates` (z "s" na końcu!).
Wewnątrz folderu templates utwórz plik i nazwij go `index.html`.
Twój projekt musi wyglądać tak:

```text
Day_47_Flask/
 ├── main.py
 └── templates/
      └── index.html
```

Krok 1: Plik templates/index.html (Czysty Frontend)
---------------------------------------------------

Wklej to do pliku HTML. 
Zwróć uwagę na te podwójne wąsy klamrowe {{ }}. 
To jest właśnie `Jinja`. 
Przeglądarka tego nie rozumie, ale Flask podmieni te wąsy na prawdziwe dane, zanim wyśle stronę do szefa.

```html
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Dashboard Firmowy</title>
</head>
<body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 50px;">
    <h1 style="color: #333;">Live Dashboard Firmowy</h1>
    
    <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 300px;">
        <!-- Tu wpadną zmienne z Pythona -->
        <h2 style="color: #0056b3;">📍 {{ city_name }}</h2>
        <p style="font-size: 24px; margin: 5px 0;">🌡️ Temperatura: <strong>{{ temperature }} °C</strong></p>
        <p style="font-size: 18px; color: #666;">☁️ Warunki: {{ weather_desc }}</p>
    </div>
</body>
</html>
```

Krok 2: Plik main.py (Czysty Backend)
-------------------------------------

Podmień swój kod w Pythonie na ten poniżej. 
Zwróć uwagę na to, że importujemy nową funkcję `render_template`.

```python
from flask import Flask, render_template
import requests

app = Flask(__name__)

API_KEY = "TUTAJ_WKLEJ_SWOJ_KLUCZ_API" 
MY_LAT = 52.5200 
MY_LONG = 13.4050

@app.route("/")
def home():
    parameters = {
        "lat": MY_LAT,
        "lon": MY_LONG,
        "appid": API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=parameters)
        response.raise_for_status()
        data = response.json()
        
        # Wyciągamy dane
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"].capitalize()
        city = data["name"]

        # MAGIA JINJA: Zamiast zwracać stringa z HTML, wywołujemy plik index.html
        # i "wstrzykujemy" do niego zmienne zadeklarowane po przecinku.
        return render_template("index.html", city_name=city, temperature=temp, weather_desc=description)

    except Exception as e:
        return f"<h1>Błąd pobierania danych z API</h1><p>{e}</p>"

if __name__ == "__main__":
    app.run(debug=True)
```

Co tu jest najważniejsze (Inżynieria pod maską):
------------------------------------------------

Separation of Concerns (Rozdział odpowiedzialności): 
To jest zasada, o którą pytają na każdej rozmowie rekrutacyjnej. 
Python odpowiada TYLKO za logikę (pobranie danych, obliczenia). 
HTML odpowiada TYLKO za wygląd. 
Nigdy ich nie mieszaj, jeśli projekt ma więcej niż 50 linijek.

render_template(): 
Ta funkcja automatycznie szuka pliku w folderze templates/. 
Jeśli nazwiesz folder inaczej (np. template), Flask wywali błąd TemplateNotFound.

Silnik Jinja ({{ }}): 
Kiedy Flask wykonuje render_template, najpierw skanuje plik index.html. 
Szuka podwójnych klamer {{ }} i wstawia w ich miejsce wartości zmiennych, 
które mu przekazałeś (city_name, temperature). 
Dopiero taki "przemielony" i gotowy HTML leci przez internet do przeglądarki.

Przetestuj to:
Zapisz oba pliki, upewnij się, że masz poprawną strukturę folderów i odśwież stronę `127.0.0.1:5000` w przeglądarce. 
Wygląda tak samo? O to chodziło! Ale pod maską to już jest profesjonalna architektura.

Działa bez błędu? Jeśli tak, to właśnie zbudowałeś fundament pod każdą nowoczesną aplikację webową 
(np. Netflix czy Spotify pod spodem działają na dokładnie tej samej zasadzie oddzielania danych od widoku).

Co teraz? 
Idąc kursem, mamy Dynamiczne ścieżki w URL – czyli jak zrobić, żebyś po wpisaniu w przeglądarce 127.0.0.1:5000/Warszawa 
dostał pogodę dla Warszawy, a po wpisaniu /Londyn dla Londynu, używając wciąż tego samego, jednego pliku index.html?



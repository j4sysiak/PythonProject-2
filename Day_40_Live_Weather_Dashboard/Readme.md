Dzień 40
--------

Day_40_Live_Weather_Dashboard
-----------------------------

Cel:
podpięcie do serwera www (Flask) bota pogodowego, żeby "serwował" pogodę w czasie rzeczywistym. 
Teraz Twój program nie tylko "odpytuje" inne serwery, ale sam staje się pełnoprawnym dostawcą danych.

Łączymy Flask (Twój serwer) z biblioteką requests (Twój bot).
Jak to działa? 
Kiedy Twój szef wpisze w przeglądarce adres Twojego serwera: 
1. Flask w ułamku sekundy odpali bota, 
2. bot poleci do OpenWeatherMap
3. pobierze aktualną temperaturę
4. Flask ubierze to w ładny kod HTML
5. wypluje na ekran szefa

Wklej ten kod do swojego main.py w projekcie Flask. 
Pamiętaj tylko, żeby wkleić swój działający klucz API w linijce API_KEY.

```python
from flask import Flask
import requests

app = Flask(__name__)

# --- KONFIGURACJA BOTA ---
API_KEY = "TUTAJ_WKLEJ_SWOJ_KLUCZ_API" 
MY_LAT = 52.5200 # Berlin
MY_LONG = 13.4050

@app.route("/")
def home():
    # 1. Bot wykonuje robotę (pobiera dane na żywo w momencie wejścia na stronę)
    parameters = {
        "lat": MY_LAT,
        "lon": MY_LONG,
        "appid": API_KEY,
        "units": "metric" # Celsjusze
    }
    
    try:
        response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=parameters)
        response.raise_for_status()
        data = response.json()
        
        # 2. Wyciągamy mięso z JSON-a
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"].capitalize()
        city = data["name"]

        # 3. Flask generuje stronę HTML z wstrzykniętymi danymi (f-string)
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 50px;">
                <h1 style="color: #333;">Live Dashboard Firmowy</h1>
                <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 300px;">
                    <h2 style="color: #0056b3;">📍 {city}</h2>
                    <p style="font-size: 24px; margin: 5px 0;">🌡️ Temperatura: <strong>{temp} °C</strong></p>
                    <p style="font-size: 18px; color: #666;">☁️ Warunki: {description}</p>
                </div>
            </body>
        </html>
        """
        return html_content

    except Exception as e:
        # Obsługa błędu - jeśli API padnie, serwer się nie zawiesi, tylko wyświetli komunikat
        return f"<h1>Błąd pobierania danych z API</h1><p>{e}</p>"

if __name__ == "__main__":
    app.run(debug=True)
```

Co tu jest najważniejsze (Inżynieria pod maską):

Przetwarzanie w locie (On-Demand): 
Zauważ, że `requests.get()` jest wewnątrz funkcji home(). 
To kluczowe. Kod nie wykonuje się raz przy starcie skryptu. 
On wykonuje się za każdym razem, gdy ktoś odświeży stronę (wciśnie F5). 
Masz 100% aktualne dane w czasie rzeczywistym.

Dynamiczny HTML (f-strings): 
To, co zwraca Flask (zmienna html_content), to czysty kod HTML, w który wstrzyknąłeś zmienne {city} i {temp}. 
Przeglądarka szefa nie wie, że to wygenerował Python. 
Ona widzi ładną, statyczną stronę z ramkami i cieniami (box-shadow).

try / except w serwerze WWW: 
To jest absolutny wymóg. 
Gdyby OpenWeatherMap padło, a Ty nie dałbyś try/except, 
Twój serwer Flask zwróciłby szefowi chamski błąd 500 Internal Server Error. 
A tak, wypluje kulturalny komunikat: "Błąd pobierania danych".

Przetestuj to:

Odpal skrypt.
Wejdź na http://127.0.0.1:5000.
Zobaczysz elegancki, nowoczesny kafelek z aktualną temperaturą w Berlinie. Odśwież stronę – bot w tle znów odpyta API.
To jest dokładnie to, co robimy w profesjonalnych systemach. 
Oddzielamy "backend" (Python odpytujący bazę/API) od "frontendu" (to co widzi użytkownik).
Działa? Masz swój własny dashboard? 
Jeśli tak, to w następnym kroku zgodnie z kursem Angeli uczymy się wyciągać ten kod HTML do osobnego pliku (szablony Jinja), 
żeby nie śmiecić w pliku .py gigantycznymi blokami tekstu. 
To ostatecznie przygotuje Cię do budowy pełnoprawnych aplikacji webowych.  


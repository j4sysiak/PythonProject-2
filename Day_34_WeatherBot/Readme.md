Dzień 34
--------

Day_33_WeatherBot
-----------------

Skoro bot wysyła maile i rozumie API, to jesteś w punkcie, w którym możesz automatyzować życie.

Zgodnie z kursem (i logiką inżynierską), następny krok to połączenie tych dwóch światów w "Automated Birthday Wisher" lub "Rain/Weather Alert".

Czego się teraz nauczysz (Dzień 34-35):

Biblioteka datetime: 
To jest absolutna podstawa. 
Każdy system w pracy opiera się na czasie (logi, raporty, harmonogramy). 
Musisz umieć sprawdzić: "Jaki jest dzisiaj dzień tygodnia?", "Czy jest godzina 8:00 rano?".

Harmonogram zadań (Cron Jobs / Task Scheduler): 
Skrypt, który odpalasz ręcznie, jest mało warty. 
Pokażę Ci, jak sprawić, żeby Twój kod sam odpalał się codziennie o 8:00 rano.

Projekt: 
"Czy dzisiaj będzie padać?" (Weather Alert)
To jest klasyk. 
Użyjemy API pogodowego `OpenWeatherMap` i wyślemy maila, tylko jeśli ma padać.

Krok 1: API Pogodowe
--------------------
Musisz się zarejestrować na OpenWeatherMap (darmowe konto) i wygenerować API Key (długi ciąg znaków).
https://home.openweathermap.org/api_keys

Key	                                       Name	           Status	       Actions
23f6c2bb4d24aff79544428507bfe5fa           Default	       Active
23b334404f2ba580f65d259a294a02d6           jacek	       Active	  


Krok 2: Kod (Esencja)
---------------------
Oto jak to wygląda w profesjonalnym wydaniu. 
Wklej to do nowego projektu Day_33_WeatherBot:

```python
import requests
import smtplib

# Twój klucz z OpenWeatherMap i parametry lokalizacji (np. dla Berlina)
API_KEY = "23f6c2bb4d24aff79544428507bfe5fa"
MY_LAT = 52.520008
MY_LONG = 13.404954

# 1. Pobieramy prognozę (OneCall API)
parameters = {
    "lat": MY_LAT,
    "lon": MY_LONG,
    "appid": API_KEY,
    "exclude": "current,minutely,daily" # Wywalamy zbędne dane, bierzemy tylko godzinowe
}

response = requests.get("https://api.openweathermap.org/data/2.5/forecast", params=parameters)
response.raise_for_status()
weather_data = response.json()

# 2. Sprawdzamy czy będzie padać w ciągu najbliższych 12 godzin
will_rain = False
for hour_data in weather_data["list"][:12]:
    condition_code = hour_data["weather"][0]["id"]
    if int(condition_code) < 700: # Kod poniżej 700 w OpenWeather to deszcz/śnieg
        will_rain = True

# 3. Jeśli pada - wysyłamy maila
if will_rain:
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user="j4sysiak@gmail.com", password="jtiztfzhnxytcivw")
        connection.sendmail(
            from_addr="j4sysiak@gmail.com",
            to_addrs="j4sysiak@gmail.com",
            msg="Subject: Weź parasol!\n\nDzisiaj będzie padać. Weź parasol!".encode('utf-8')
        )
    print("Mail wysłany!")
```

Dlaczego to jest ważne?
-----------------------

parameters: 
Zobacz jak elegancko przekazujemy dane do API. 
Pandas i requests kochają słowniki. 
Nie doklejasz zmiennych do URL stringa ręcznie, tylko wrzucasz je do słownika params. 
To chroni przed błędami.

Logika biznesowa: 
To nie jest już tylko "wyświetl wynik". 
To jest skrypt, który podejmuje decyzję (if will_rain:). 
To jest definicja automatyzacji.

Jak to odpalać "na stałe"? (To jest najważniejsze pytanie)
----------------------------------------------------------

Nie będziesz przecież siedział przy komputerze i klikał Run co rano.

Na Windowsie: 
Używasz Task Scheduler (Harmonogram zadań). 
Klikasz "Utwórz zadanie", wskazujesz plik .exe interpretera Pythona (tego z Twojego folderu .venv) i jako argument podajesz ścieżkę do main.py.

Na serwerze (Linux): 
Używasz Cron. 
Piszesz jedną linijkę w systemie, np. 0 8 * * * /usr/bin/python3 /home/user/script.py i serwer sam odpala to codziennie o 8:00 rano.

Co dalej?
Jeśli to działa, masz już kompletne umiejętności juniora. 
Dalej w kursie jest `Web Scraping` (BeautifulSoup – wyciąganie danych z gotowych stron WWW, które nie mają API).

Chcesz wjechać w Web Scraping, czy chcesz, żebym Ci pokazał jak z tego skryptu zrobić plik.exe, który wyślesz komukolwiek i zadziała bez Pythona?


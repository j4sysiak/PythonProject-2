Dzień 32
--------

Day_32_API__Application_Programming_Interface
---------------------------------------------

To jest moment, w którym Twój program przestaje być zamknięty w Twoim komputerze i zaczyna "rozmawiać" z serwerami na całym świecie.

Angela w tym dniu pokazuje jak pobrać dane o tym, gdzie aktualnie znajduje się Międzynarodowa Stacja Kosmiczna (ISS). 
My zrobimy to samo, ale w wersji inżynierskiej – bez zbędnego gadania o "kosmosie", skupimy się na mechanice.

Teoria w 2 zdaniach:
--------------------

API: 
To "kelner" w restauracji. 
Ty (klient) wysyłasz żądanie (zamówienie), kelner idzie do kuchni (serwer), bierze dane i przynosi Ci je w formacie np `JSON`.

Biblioteka requests: 
To standard branżowy do wysyłania zapytań do internetu.

Krok 1: Instalacja
------------------

Otwórz terminal w PyCharmie i wpisz:
`pip install requests`

Projekt: Gdzie jest ISS? (Pobieranie danych z sieci)

Utwórz projekt Day_32_API. Wklej to do main.py:

```python
# 1. Wysyłamy zapytanie (GET request) do serwera
# Serwer zwraca nam odpowiedź (Response)
response = requests.get(url="http://api.open-notify.org/iss-now.json")

# 2. Sprawdzanie czy serwer odpowiedział poprawnie (kod 200 = OK)
# Jeśli serwer padł, rzucamy błąd (raise_for_status)
response.raise_for_status()

# 3. Wyciągamy dane w formacie JSON (Python zamienia to automatycznie na słownik)
data = response.json()

# 4. Wyciągamy konkretne dane, które nas interesują
longitude = data["iss_position"]["longitude"]
latitude = data["iss_position"]["latitude"]

print(f"Stacja ISS jest teraz nad punktem: {latitude}, {longitude}")
```


Co tu jest najważniejsze (Inżynieria):
--------------------------------------

requests.get(): 
To jest fundament. 
Wpisujesz adres URL, a Python wysyła sygnał do serwera.

raise_for_status(): 
To jest najważniejsza linijka w tym kodzie. 
Jeśli serwer zwróci błąd (np. 404 - nie znaleziono, albo 500 - serwer padł), 
ten kod automatycznie przerwie działanie programu i powie Ci, co jest nie tak. 
Nigdy nie pisz kodu z API bez tej linijki.

response.json(): 
Serwer wysyła dane jako długi ciąg znaków (tekst). 
Metoda `.json()` to "magiczny przycisk", który zamienia ten tekst na czytelny dla Pythona słownik.

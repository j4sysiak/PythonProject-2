import requests

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

# Stacja ISS jest teraz nad punktem: 42.5925, 158.8926
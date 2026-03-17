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
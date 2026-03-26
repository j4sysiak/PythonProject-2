import requests
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

URL = "http://localhost:8000/transfer"
PAYLOAD = {
    "from_account_id": 3,  #  -------> Uwaga, tutaj wpisz ID swojego konta nr 1 (Jan Kowalski)
    "to_account_id": 4,    #  -------> Uwaga, tutaj wpisz ID swojego konta nr 2 (Adam Nowak)
    "amount": 10.0  # Przelewamy 10 zł
}


def make_transfer():
    response = requests.post(URL, json=PAYLOAD)

    # Jeśli status to nie 200 (OK) i nie 400 (Brak środków), pokaż nam co się stało!
    if response.status_code not in [200, 400]:
        print(f"Nieoczekiwany status {response.status_code}: {response.text}")

    return response.status_code


print("Rozpoczynamy atak współbieżny: 50 przelewów naraz...")

with ThreadPoolExecutor(max_workers=50) as executor:
    results = list(executor.map(lambda _: make_transfer(), range(50)))

# Zliczamy i wyświetlamy WSZYSTKIE kody HTTP, jakie zwrócił serwer
print("\n--- PODSUMOWANIE STATUSÓW ---")
for status_code, count in Counter(results).items():
    print(f"Status HTTP {status_code}: wystąpił {count} razy")
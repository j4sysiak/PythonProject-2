#!/usr/bin/env python3
"""
Skrypt do testowania Optimistic Locking dla endpointu /transfer.

Co robi:
- tworzy dwa konta testowe via POST /accounts (jeśli istnieją, tworzy nowe)
- uruchamia N równoległych przelewów z konta A do B
- zlicza odpowiedzi: 200 (success), 409 (conflict - OCC), 400 (bad request / insufficient funds) i inne
- po przebiegu pobiera salda kont i wypisuje raport

Uruchomienie:
  - Upewnij się, że aplikacja działa na http://localhost:8000 lub ustaw env BASE_URL
  - python MiniBank/tests/load_test_optimistic.py

Uwaga: skrypt używa modułu `requests`. Jeśli nie masz go w venv, zainstaluj: pip install requests
"""



# URUCHOMIENIE:
# Set-Location C:\dev\python-projects\PycharmProjects\PythonProject-2
# .\.venv\Scripts\Activate.ps1
# python -m MiniBank.tests.load_test_optimistic

import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import random
import requests

# Konfiguracja
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")
ACCOUNTS_ENDPOINT = f"{BASE_URL}/accounts"
TRANSFER_ENDPOINT = f"{BASE_URL}/transfer"
GET_ACCOUNT_ENDPOINT = lambda acc_id: f"{BASE_URL}/accounts/{acc_id}"

# Parametry testu
NUM_REQUESTS = 50
MAX_WORKERS = 50
TRANSFER_AMOUNT = 10.0
RETRY_ON_CONFLICT = 3


def create_account(owner_name: str, initial_balance: float = 1000.0, currency: str = "PLN"):
    payload = {
        "owner_name": owner_name,
        "initial_balance": initial_balance,
        "currency": currency,
    }
    r = requests.post(ACCOUNTS_ENDPOINT, json=payload, timeout=5)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Create account failed: {r.status_code} {r.text}")
    return r.json()


def get_account(acc_id: int):
    r = requests.get(GET_ACCOUNT_ENDPOINT(acc_id), timeout=5)
    if r.status_code == 200:
        return r.json()
    return None


def do_transfer(session: requests.Session, from_id: int, to_id: int, amount: float, retries=RETRY_ON_CONFLICT):
    payload = {
        "from_account_id": from_id,
        "to_account_id": to_id,
        "amount": amount,
    }

    for attempt in range(1, retries + 1):
        try:
            r = session.post(TRANSFER_ENDPOINT, json=payload, timeout=10)
        except Exception as e:
            return ("error", str(e))

        if r.status_code == 200:
            return (200, r.json())
        if r.status_code == 409:
            # konflikt optimistic locking — spróbuj ponownie z małym backoffem
            if attempt < retries:
                time.sleep(0.01 + random.random() * 0.05)
                continue
            return (409, r.text)
        # inne statusy (400 np. insufficient funds)
        return (r.status_code, r.text)


def main():
    print("BASE_URL:", BASE_URL)

    # 1) Utwórz testowe konta
    owner_a = f"LoadTest-A-{uuid.uuid4().hex[:6]}"
    owner_b = f"LoadTest-B-{uuid.uuid4().hex[:6]}"

    print("Creating accounts...")
    a = create_account(owner_a, initial_balance=1000.0)
    b = create_account(owner_b, initial_balance=0.0)

    a_id = int(a.get("id") or a.get("account_id") or a.get("accountId") or a.get("id", 0))
    b_id = int(b.get("id") or b.get("account_id") or b.get("accountId") or b.get("id", 0))

    print(f"Account A: id={a_id}, owner={owner_a}")
    print(f"Account B: id={b_id}, owner={owner_b}")

    # 2) Wykonaj wiele równoległych transferów
    results = []
    print(f"Starting {NUM_REQUESTS} concurrent transfers of {TRANSFER_AMOUNT} from {a_id} -> {b_id} ...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = []
        session = requests.Session()
        for _ in range(NUM_REQUESTS):
            futures.append(ex.submit(do_transfer, session, a_id, b_id, TRANSFER_AMOUNT))

        for fut in as_completed(futures):
            try:
                results.append(fut.result())
            except Exception as e:
                results.append(("error", str(e)))

    # 3) Podsumowanie
    counter = Counter([r[0] for r in results])
    print("\n--- PODSUMOWANIE ---")
    for k, v in counter.items():
        print(f"Status {k}: {v}")

    # 4) Finalne salda
    print("\nPobieram finalne salda kont...")
    a_info = get_account(a_id)
    b_info = get_account(b_id)

    print("Account A info:", a_info)
    print("Account B info:", b_info)


if __name__ == "__main__":
    main()


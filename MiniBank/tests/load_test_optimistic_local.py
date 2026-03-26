#!/usr/bin/env python3
"""
Wersja lokalna testu Optimistic Locking: uruchamia ASGI app w-process
i używa httpx.AsyncClient aby dokonywać wielu równoległych żądań bez sieci.

Ten skrypt USTAWIA przed importem aplikacji zmienną środowiskową
DATABASE_URL na lokalny plik SQLite (test_minibank.db) — dzięki temu
wszystkie zapisy trafią do pliku testowego, nie do produkcyjnego Postgresa.

Uruchomienie (PowerShell):
  Set-Location <project_root>
  .\.venv\Scripts\python -m MiniBank.tests.load_test_optimistic_local

Wymaga: httpx
"""




# URUCHOMIENIE:
# Set-Location C:\dev\python-projects\PycharmProjects\PythonProject-2
# .\.venv\Scripts\Activate.ps1
# .\.venv\Scripts\python -m MiniBank.tests.load_test_optimistic_local

import os
import asyncio
import uuid
import random
from collections import Counter

# Ustaw zmienną środowiskową na testowy sqlite (musimy to zrobić PRZED importem aplikacji)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
TEST_DB = os.path.join(PROJECT_ROOT, "test_minibank.db")
# Force using test sqlite DB for this script (override any external DATABASE_URL)
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB}"
os.environ.setdefault("ANYIO_BACKEND", "asyncio")

from httpx import AsyncClient, ASGITransport

# Import aplikacji po ustawieniu DATABASE_URL
from MiniBank.main import app

# Parametry testu
NUM_REQUESTS = 50
MAX_CONCURRENCY = 50
TRANSFER_AMOUNT = 10.0
RETRY_ON_CONFLICT = 3


async def create_account(client: AsyncClient, owner_name: str, initial_balance: float = 1000.0):
    r = await client.post("/accounts", json={"owner_name": owner_name, "initial_balance": initial_balance, "currency": "PLN"})
    r.raise_for_status()
    return r.json()


async def get_account(client: AsyncClient, acc_id: int):
    r = await client.get(f"/accounts/{acc_id}")
    if r.status_code == 200:
        return r.json()
    return None


async def do_transfer(client: AsyncClient, from_id: int, to_id: int, amount: float, retries=RETRY_ON_CONFLICT):
    payload = {"from_account_id": from_id, "to_account_id": to_id, "amount": amount}
    for attempt in range(1, retries + 1):
        try:
            r = await client.post("/transfer", json=payload, timeout=10.0)
        except Exception as e:
            return ("error", str(e))

        if r.status_code == 200:
            return (200, r.json())
        if r.status_code == 409:
            if attempt < retries:
                await asyncio.sleep(0.01 + random.random() * 0.05)
                continue
            return (409, r.text)
        return (r.status_code, r.text)


async def run():
    print("Using test DB:", os.environ.get("DATABASE_URL"))
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # create accounts
        owner_a = f"LocalLoad-A-{uuid.uuid4().hex[:6]}"
        owner_b = f"LocalLoad-B-{uuid.uuid4().hex[:6]}"
        print("Creating accounts...")
        a = await create_account(client, owner_a, initial_balance=1000.0)
        b = await create_account(client, owner_b, initial_balance=0.0)

        a_id = int(a.get("id") or a.get("account_id") or 0)
        b_id = int(b.get("id") or b.get("account_id") or 0)
        print(f"Account A id={a_id}, B id={b_id}")

        sem = asyncio.Semaphore(MAX_CONCURRENCY)

        async def worker():
            async with sem:
                return await do_transfer(client, a_id, b_id, TRANSFER_AMOUNT)

        tasks = [asyncio.create_task(worker()) for _ in range(NUM_REQUESTS)]
        results = await asyncio.gather(*tasks)

        counter = Counter([r[0] for r in results])
        print("\n--- PODSUMOWANIE ---")
        for k, v in counter.items():
            print(f"Status {k}: {v}")

        print("\nPobieram finalne salda kont...")
        a_info = await get_account(client, a_id)
        b_info = await get_account(client, b_id)
        print("Account A info:", a_info)
        print("Account B info:", b_info)


if __name__ == "__main__":
    asyncio.run(run())


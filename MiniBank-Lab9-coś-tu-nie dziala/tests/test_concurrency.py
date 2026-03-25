import pytest
from concurrent.futures import ThreadPoolExecutor


@pytest.mark.asyncio
async def test_optimistic_locking_conflict(client):
    # 1. SETUP: Konto z saldem 100
    payload = {"owner_name": "Testowy User", "initial_balance": 100.0, "currency": "PLN"}
    account_id = client.post("/accounts", json=payload).json()["id"]

    # 2. Funkcja wysyłająca przelew
    def send_transfer():
        return client.post("/convert-transfer", json={
            "from_account_id": account_id,
            "to_account_id": 0,
            "amount": 10.0
        })

    # 3. ATAK: Odpalamy 2 przelewy dokładnie w tym samym czasie
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: send_transfer(), range(2)))

    # 4. WERYFIKACJA
    status_codes = [r.status_code for r in results]
    print(f"\nOtrzymane kody: {status_codes}")

    # Jeden musi przejść (200), a drugi musi dostać konflikt (409)
    assert 200 in status_codes
    assert 409 in status_codes
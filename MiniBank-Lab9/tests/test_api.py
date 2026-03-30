def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_create_account(client):
    payload = {
        "owner_name": "Testowy User",
        "initial_balance": 500.0,
        "currency": "PLN"
    }
    response = client.post("/accounts", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["owner_name"] == "Testowy User"
    # Porównujemy tekst z tekstem (bez rzutowania na float)
    assert data["balance"] == "500.00"


def test_transfer_money_successfull(client):
    # Tworzymy konta
    acc1 = client.post("/accounts", json={"owner_name": "Marek", "initial_balance": 500.0, "currency": "PLN"}).json()
    acc2 = client.post("/accounts", json={"owner_name": "Wacek", "initial_balance": 0.0, "currency": "PLN"}).json()

    # Transfer
    transfer_payload = {
        "from_account_id": acc1["id"],
        "to_account_id": acc2["id"],
        "amount": 100.0
    }
    response = client.post("/transfer", json=transfer_payload)
    assert response.status_code == 200


def test_transfer_insufficient_funds(client):
    # Tworzymy konta
    acc1 = client.post("/accounts", json={"owner_name": "Adam", "initial_balance": 50.0, "currency": "PLN"}).json()
    acc2 = client.post("/accounts", json={"owner_name": "Bartek", "initial_balance": 0.0, "currency": "PLN"}).json()

    # Transfer
    transfer_payload = {
        "from_account_id": acc1["id"],
        "to_account_id": acc2["id"],
        "amount": 100.0
    }
    response = client.post("/convert-transfer", json=transfer_payload)
    assert response.status_code == 400


def test_transaction_adding_money_successfull(client):
    # Tworzymy konto
    acc1 = client.post("/accounts", json={"owner_name": "Edek", "initial_balance": 0.0, "currency": "PLN"}).json()

    # transaction
    transaction_payload = {
        "from_account_id" :0,
        "to_account_id": acc1["id"],
        "amount": 100.0
    }
    response = client.post("/transaction", json=transaction_payload)
    assert response.status_code == 200


def test_transaction_withdrowal_money_successfull(client):
    # Tworzymy konto
    acc1 = client.post("/accounts", json={"owner_name": "Alfred", "initial_balance": 111.0, "currency": "PLN"}).json()

    # transaction
    transaction_payload = {
        "from_account_id": acc1["id"],
        "to_account_id": 0,
        "amount": 110.0
    }
    response = client.post("/transaction", json=transaction_payload)
    assert response.status_code == 200


def test_convert_money_successfull(client):
    # Tworzymy konta
    acc1 = client.post("/accounts", json={"owner_name": "Ilona", "initial_balance": 1500.0, "currency": "PLN"}).json()
    acc2 = client.post("/accounts", json={"owner_name": "Marry", "initial_balance": 0.0, "currency": "USD"}).json()

    # convert-transfer
    convert_payload = {
        "from_account_id": acc1["id"],
        "to_account_id": acc2["id"],
        "amount": 88.0
    }
    response = client.post("/convert-transfer", json=convert_payload)
    assert response.status_code == 200


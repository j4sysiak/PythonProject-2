import requests

# To jest serwis zewnętrzny wyciagajacy rate'ing walut, izolujemy go od glównej logiki
def get_exchange_rate(from_curr, to_curr):
    # Używamy darmowego API (np. Frankfurter lub podobne)
    url = f"https://api.frankfurter.app/latest?from={from_curr}&to={to_curr}"
    response = requests.get(url)
    data = response.json()
    return data['rates'][to_curr]
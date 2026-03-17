from flask import Flask

# 1. Tworzymy instancję aplikacji Flask
app = Flask(__name__)

# 2. Definiujemy "trasę" (Route) - czyli adres URL
@app.route("/")
def home():
    # To, co tu zwrócisz, pokaże się w przeglądarce
    return "<h1>Witaj na moim własnym serwerze www!</h1><p>To działa po męsku.</p>"

# 3. Dodajemy drugą trasę
@app.route("/api/pogoda")
def pogoda():
    return {"miasto": "Berlin", "temp": 15.7}

# 4. Uruchamiamy serwer (tylko jeśli ten plik jest odpalany bezpośrednio)
if __name__ == "__main__":
    app.run(debug=True)
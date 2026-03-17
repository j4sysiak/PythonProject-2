from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

app = Flask(__name__)
API_KEY = "23f6c2bb4d24aff79544428507bfe5fa"

# --- 1. KONFIGURACJA BAZY DANYCH ---
# Mówimy Flaskowi, że nasza baza to plik SQLite o nazwie 'weather_history.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather_history.db'
db = SQLAlchemy(app)


# --- 2. MODEL TABELI (Jak wygląda nasz arkusz w bazie) ---
class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unikalny numer ID (Auto-inkrementacja)
    city = db.Column(db.String(100), nullable=False)  # Nazwa miasta (max 100 znaków)
    temp = db.Column(db.Float, nullable=False)  # Temperatura
    date = db.Column(db.String(100), nullable=False)  # Data i godzina wyszukiwania


# Tworzenie pliku bazy danych (uruchomi się tylko raz, jeśli pliku jeszcze nie ma)
with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def home():
    # ZAWSZE pobieramy z bazy 5 ostatnich wyszukiwań (sortowane malejąco po ID)
    history = db.session.query(SearchHistory).order_by(SearchHistory.id.desc()).limit(5).all()

    if request.method == "POST":
        city = request.form.get("city_input")

        parameters = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

        try:
            response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=parameters)
            response.raise_for_status()
            data = response.json()

            temp = data["main"]["temp"]
            description = data["weather"][0]["description"].capitalize()
            official_city_name = data["name"]

            # --- 3. ZAPIS DO BAZY DANYCH ---
            # Tworzymy nowy "obiekt" w Pythonie
            new_search = SearchHistory(
                city=official_city_name,
                temp=temp,
                date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            # Dodajemy go do sesji i komitujemy (wysyłamy trwale do bazy)
            db.session.add(new_search)
            db.session.commit()

            # Odświeżamy zmienną history, żeby tabela na stronie zaktualizowała się od razu
            history = db.session.query(SearchHistory).order_by(SearchHistory.id.desc()).limit(5).all()

            return render_template("index.html", city_name=official_city_name, temperature=temp,
                                   weather_desc=description, history=history)

        except requests.exceptions.HTTPError:
            return render_template("index.html", error=f"Nie znaleziono miasta: {city}", history=history)
        except Exception as e:
            return render_template("index.html", error=f"Błąd serwera: {e}", history=history)

    return render_template("index.html", history=history)


if __name__ == "__main__":
    app.run(debug=True)
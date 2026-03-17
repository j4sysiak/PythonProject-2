from flask import Flask, render_template, request
import requests

app = Flask(__name__)
API_KEY = "23f6c2bb4d24aff79544428507bfe5fa"


# Dodajemy obsługę metod GET i POST
@app.route("/", methods=["GET", "POST"])
def home():
    # 1. Jeśli użytkownik WCHODZI na stronę (GET), pokazujemy mu tylko pusty formularz
    if request.method == "GET":
        return render_template("index.html")

    # 2. Jeśli użytkownik KLIKNĄŁ przycisk (POST), przechwytujemy dane i odpytujemy API
    if request.method == "POST":
        # 'city_input' to dokładnie ten sam 'name', który wpisaliśmy w <input> w HTML!
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

            # Zwracamy ten sam szablon, ale tym razem Z DANYMI (więc Jinja pokaże kafelek)
            return render_template("index.html", city_name=official_city_name, temperature=temp,
                                   weather_desc=description)

        except requests.exceptions.HTTPError:
            # Jeśli API zwróci 404 (nie ma takiego miasta), przekazujemy błąd do HTML
            return render_template("index.html", error=f"Nie znaleziono miasta: {city}")
        except Exception as e:
            return render_template("index.html", error=f"Błąd serwera: {e}")
    return None


if __name__ == "__main__":
    app.run(debug=True)
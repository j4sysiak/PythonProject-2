from flask import Flask, render_template
import requests

app = Flask(__name__)

API_KEY = "23f6c2bb4d24aff79544428507bfe5fa"


# 1. DYNAMICZNA TRASA: Znak < > mówi Flaskowi: "Cokolwiek user wpisze po ukośniku,
# wrzuć to do zmiennej city_name i przekaż do funkcji".
@app.route("/<city_name>")
def get_weather(city_name):
    # 2. Zmieniamy parametry API. Zamiast lat/lon, używamy "q" (Query), czyli nazwy miasta.
    parameters = {
        "q": city_name,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=parameters)
        response.raise_for_status()
        data = response.json()

        # Wyciągamy dane dokładnie tak samo
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"].capitalize()
        # Bierzemy oficjalną nazwę miasta z API (żeby np. "londyn" zamieniło na ładne "London")
        official_city_name = data["name"]

        # 3. Zwracamy ten sam szablon, wstrzykując nowe dane
        return render_template("index.html", city_name=official_city_name, temperature=temp, weather_desc=description)

    # Co jeśli ktoś wpisze miasto, którego nie ma (np. /Nibylandia)? API zwróci błąd 404!
    except requests.exceptions.HTTPError:
        return f"<h1>Błąd 404</h1><p>Nie znaleziono miasta: <b>{city_name}</b>. Sprawdź literówkę w adresie.</p>"
    except Exception as e:
        return f"<h1>Błąd serwera</h1><p>{e}</p>"


if __name__ == "__main__":
    app.run(debug=True)
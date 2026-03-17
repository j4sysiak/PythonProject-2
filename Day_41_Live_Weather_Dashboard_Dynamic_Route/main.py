from flask import Flask, render_template
import requests

app = Flask(__name__)

API_KEY = "23f6c2bb4d24aff79544428507bfe5fa"
MY_LAT = 52.5200
MY_LONG = 13.4050


@app.route("/")
def home():
    parameters = {
        "lat": MY_LAT,
        "lon": MY_LONG,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=parameters)
        response.raise_for_status()
        data = response.json()

        # Wyciągamy dane
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"].capitalize()
        city = data["name"]

        # MAGIA JINJA: Zamiast zwracać stringa z HTML, wywołujemy plik index.html
        # i "wstrzykujemy" do niego zmienne zadeklarowane po przecinku.
        return render_template("index.html", city_name=city, temperature=temp, weather_desc=description)

    except Exception as e:
        return f"<h1>Błąd pobierania danych z API</h1><p>{e}</p>"


if __name__ == "__main__":
    app.run(debug=True)
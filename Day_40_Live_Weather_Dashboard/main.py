from flask import Flask
import requests
app = Flask(__name__)

# --- KONFIGURACJA BOTA ---
API_KEY = "23f6c2bb4d24aff79544428507bfe5fa"
MY_LAT = 52.5200  # Berlin
MY_LONG = 13.4050


@app.route("/")
def home():
    # 1. Bot wykonuje robotę (pobiera dane na żywo w momencie wejścia na stronę)
    parameters = {
        "lat": MY_LAT,
        "lon": MY_LONG,
        "appid": API_KEY,
        "units": "metric"  # Celsjusze
    }

    try:
        response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=parameters)
        response.raise_for_status()
        data = response.json()

        # 2. Wyciągamy mięso z JSON-a
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"].capitalize()
        city = data["name"]

        # 3. Flask generuje stronę HTML z wstrzykniętymi danymi (f-string)
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 50px;">
                <h1 style="color: #333;">Live Dashboard Firmowy</h1>
                <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 300px;">
                    <h2 style="color: #0056b3;">📍 {city}</h2>
                    <p style="font-size: 24px; margin: 5px 0;">🌡️ Temperatura: <strong>{temp} °C</strong></p>
                    <p style="font-size: 18px; color: #666;">☁️ Warunki: {description}</p>
                </div>
            </body>
        </html>
        """
        return html_content

    except Exception as e:
        # Obsługa błędu - jeśli API padnie, serwer się nie zawiesi, tylko wyświetli komunikat
        return f"<h1>Błąd pobierania danych z API</h1><p>{e}</p>"


if __name__ == "__main__":
    app.run(debug=True)
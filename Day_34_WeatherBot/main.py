import requests
import smtplib

# Twój klucz z OpenWeatherMap i parametry lokalizacji (np. dla Berlina)
API_KEY = "23f6c2bb4d24aff79544428507bfe5fa"
# API_KEY = "23b334404f2ba580f65d259a294a02d6"
MY_LAT = 52.520008
MY_LONG = 13.404954

# 1. Pobieramy prognozę (OneCall API)
parameters = {
    "lat": MY_LAT,
    "lon": MY_LONG,
    "appid": API_KEY,
    "exclude": "current,minutely,daily", # To jest potrzebne dla forecast
    "units": "metric"
}

response = requests.get("https://api.openweathermap.org/data/2.5/forecast", params=parameters)
response.raise_for_status()
weather_data = response.json()

# 2. Sprawdzamy czy będzie padać w ciągu najbliższych 12 godzin
will_rain = False
for hour_data in weather_data["list"][:12]:
    condition_code = hour_data["weather"][0]["id"]
    if int(condition_code) < 700: # Kod poniżej 700 w OpenWeather to deszcz/śnieg
        will_rain = True

# 3. Jeśli pada - wysyłamy maila
if will_rain:
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user="j4sysiak@gmail.com", password="jtiztfzhnxytcivw")
        connection.sendmail(
            from_addr="j4sysiak@gmail.com",
            to_addrs="j4sysiak@gmail.com",
            msg="Subject: Weź parasol!\n\nDzisiaj będzie padać. Weź parasol!".encode('utf-8')
        )
    print("Mail wysłany!")
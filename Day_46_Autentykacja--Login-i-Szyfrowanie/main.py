from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bardzo-tajny-klucz-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather_history.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Gdzie ma przekierować niezalogowanego usera?

API_KEY = "23f6c2bb4d24aff79544428507bfe5fa"


# --- BAZA DANYCH ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100))
    temp = db.Column(db.Float)
    date = db.Column(db.String(100))


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        new_admin = User(username="admin", password=generate_password_hash("haslo123"))
        db.session.add(new_admin)
        db.session.commit()


# --- TRASY ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get("username")).first()
        if user and check_password_hash(user.password, request.form.get("password")):
            login_user(user)
            return redirect(url_for('home'))
        flash("Złe dane logowania!")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user() # Ta funkcja z Flask-Login niszczy ciasteczko sesji w przeglądarce
    return redirect(url_for('login')) # Wyrzucamy usera z powrotem do ekranu logowania

@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    # Pobieramy historię z bazy
    history = db.session.query(SearchHistory).order_by(SearchHistory.id.desc()).limit(5).all()

    if request.method == "POST":
        city = request.form.get("city_input")
        parameters = {"q": city, "appid": API_KEY, "units": "metric"}

        try:
            response = requests.get("https://api.openweathermap.org/data/2.5/weather", params=parameters)
            response.raise_for_status()
            data = response.json()

            temp = data["main"]["temp"]
            description = data["weather"][0]["description"].capitalize()
            city_name = data["name"]

            # Zapis do bazy
            new_search = SearchHistory(city=city_name, temp=temp, date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            db.session.add(new_search)
            db.session.commit()

            # Odświeżamy historię po dodaniu
            history = db.session.query(SearchHistory).order_by(SearchHistory.id.desc()).limit(5).all()
            return render_template("index.html", city_name=city_name, temperature=temp, weather_desc=description,
                                   history=history)

        except Exception as e:
            return render_template("index.html", error=f"Błąd: {e}", history=history)

    return render_template("index.html", history=history)




if __name__ == "__main__":
    app.run(debug=True)
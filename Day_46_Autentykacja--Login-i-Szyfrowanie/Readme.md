Dzień 46
--------

Day_46_Autentykacja--Login-i-Szyfrowanie
----------------------------------------

Robimy "Autentykację" - zabezpieczymy Twój Dashboard hasłem. 
Dodamy formularz logowania, żeby nikt obcy nie mógł dopisywać miast do bazy, tylko Ty jako "Admin".

Masz już bazę danych, masz formularze (POST), teraz tylko dodamy sprawdzanie hasła. 
To sprawi, że Twój Dashboard z pogodą stanie się bezpiecznym narzędziem firmowym.
Wchodzimy w bezpieczne logowanie użytkownika (z szyfrowaniem haseł `Werkzeug`)? 

Do tej pory każdy mógł wpisać miasto i dodać rekord do bazy. 
W prawdziwej firmie masz poziomy dostępu. 
Teraz zrobimy "Admin Panel".

Kluczowa zasada: 
Nigdy, przenigdy nie zapisuj haseł w bazie jako "czysty tekst". 
Użyjemy biblioteki `werkzeug.security` (wbudowana we Flaska), która zamienia hasło w nieodwracalny bełkot (tzw. hash).

Krok 1: Instalacja
------------------

`pip install flask-login` (biblioteka do zarządzania sesją użytkownika).

Krok 2: Kod logowania (main.py) - Esencja
-----------------------------------------

Musisz zaimportować `generate_password_hash` oraz `check_password_hash`.

```python
from werkzeug.security import generate_password_hash, check_password_hash

# 1. ZAPISYWANIE HASŁA DO BAZY (Rejestracja)
# Kiedy tworzysz usera, nie zapisujesz 'haslo123', tylko hash:
hash_to_save = generate_password_hash("haslo123", method='pbkdf2:sha256', salt_length=8)
# Teraz w bazie (w kolumnie 'password') ląduje bełkot typu: pbkdf2:sha256:600000$....

# 2. SPRAWDZANIE HASŁA (Logowanie)
# Kiedy user wpisuje 'haslo123', program sprawdza czy hasz się zgadza:
if check_password_hash(saved_password_from_db, "haslo123"):
    print("Logowanie udane!")
else:
    print("Złe hasło!")
```

Dlaczego to jest inżynierski standard?

Salt (Sól): 
`salt_length=8` dodaje losowe znaki do hasła przed haszowaniem. 
Dzięki temu nawet jeśli dwóch użytkowników ma to samo hasło "admin123", w bazie będą wyglądać zupełnie inaczej. 
Jeśli ktoś ukradnie Ci bazę, nie da się tak łatwo wyliczyć haseł metodą "tęczowych tablic".

Flask-Login: 
To narzędzie zarządza "ciasteczkami" w przeglądarce. 
Jak raz się zalogujesz, Flask pamięta Twoją sesję, więc nie musisz się logować przy każdym odświeżeniu strony.



Praktyczne zadanie:
-------------------

Zbudujemy "Bramkę Wejściową" do Twojego serwera.
Obecnie każdy może wejść na 127.0.0.1:5000/ i dodać miasto do Twojej bazy. 
Zabezpieczymy to tak: 
strona główna będzie dostępna tylko dla zalogowanego użytkownika. 
Jeśli nie jesteś zalogowany, serwer przekieruje Cię na stronę logowania.

Krok 1: Instalacja niezbędnych narzędzi
---------------------------------------
W terminalu PyCharma:
`pip install flask-login flask-wtf email-validator`

Krok 2: Modyfikacja bazy (main.py)
----------------------------------

Musimy dodać tabelę User. 
Zastąp swój obecny `main.py` tym kodem. 
Uwaga: 
Jeśli już masz plik `weather_history.db` w folderze instance, po prostu go usuń przed startem, żeby skrypt stworzył nową tabelę `User`.

```python
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bardzo-tajny-klucz-123' # Musi być do sesji
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather_history.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)

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
    # Stwórzmy admina "na twardo" przy starcie, jeśli nie istnieje
    if not User.query.filter_by(username="admin").first():
        new_admin = User(username="admin", password=generate_password_hash("haslo123"))
        db.session.add(new_admin)
        db.session.commit()

# --- TRASY (ROUTES) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get("username")).first()
        if user and check_password_hash(user.password, request.form.get("password")):
            login_user(user)
            return redirect(url_for('home'))
        flash("Złe dane logowania!")
    return render_template("login.html")

@app.route("/", methods=["GET", "POST"])
@login_required # <--- TO JEST KLUCZ: tylko zalogowani widzą pogodę
def home():
    # ... [TUTAJ TWOJA LOGIKA POGODOWA Z POPRZEDNIEGO KROKU] ...
    return render_template("index.html", history=history)

if __name__ == "__main__":
    app.run(debug=True)
```

Skoro już wiesz, że trzyma Cię sesja, musimy dać Ci możliwość jej "zabicia". 
W profesjonalnej aplikacji zawsze musi być przycisk wylogowania.
Dopisz tę funkcję w main.py (gdziekolwiek pod innymi trasami):




```python
from flask_login import logout_user # Upewnij się, że masz to zaimportowane na górze!

-----> tu jest endpoint do logowania <-----

@app.route("/logout")
@login_required
def logout():
    logout_user() # Ta funkcja z Flask-Login niszczy ciasteczko sesji w przeglądarce
    return redirect(url_for('login')) # Wyrzucamy usera z powrotem do ekranu logowania

-----> reszta Twojego kodu <-----

```


Krok 3: Nowy szablon templates/login.html
-----------------------------------------

Musisz stworzyć ten plik. To jest Twoja "bramka".

```html
<!DOCTYPE html>
<html>
<body>
    <h2>Logowanie do Dashboardu</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Login" required>
        <input type="password" name="password" placeholder="Hasło" required>
        <button type="submit">Zaloguj</button>
    </form>
    {% with messages = get_flashed_messages() %}
      {% if messages %} {{ messages[0] }} {% endif %}
    {% endwith %}
</body>
</html>
```

Dodaj przycisk wylogowania w templates/index.html:
Na samej górze pliku `index.html`, zaraz pod tagiem <body>, wklej ten mały guzik:

```html
<div style="text-align: right;">
    <a href="/logout" style="text-decoration: none; padding: 10px; background-color: #dc3545; color: white; border-radius: 5px;">Wyloguj się</a>
</div>
```


Dlaczego to jest inżynierskie rozwiązanie:
------------------------------------------

@login_required: 
To jest "strażnik".
Jeśli spróbujesz wejść na / bez ciasteczka sesji, Flask automatycznie wykopie Cię na stronę /login.

UserMixin: 
To magia Flask-Login. 
Dzięki temu klasa User automatycznie wie, czy jest "zalogowana", "aktywna" itd., nie musisz pisać tego ręcznie.

login_manager: 
To jest menedżer, który pilnuje sesji w przeglądarce. 
Bez niego po zalogowaniu, przy odświeżeniu strony, zapomniałby, że jesteś adminem.

Zadanie:
--------
1. Odpal serwer.
2. Wejdź na http://127.0.0.1:5000/. Zostaniesz wykopany do /login
3. Wpisz admin / haslo123.
4. Jeśli hasło jest poprawne -> witaj w dashboardzie pogodowym.
5. Możesz sobie teraz dodawać miasta, ale tylko Ty, bo jesteś zalogowany jako admin.
6. Wejdź na http://127.0.0.1:5000/logout
7. Kliknij czerwony przycisk "Wyloguj się" w prawym górnym rogu.
8. System usunie Twoje ciasteczko i wykopie Cię na stronę logowania.
9. Spróbuj teraz z palca wpisać w pasku adresu http://127.0.0.1:5000/. 
10. Serwer znowu skopie Ci tyłek i cofnie do logowania, bo nie masz już uprawnień.


Teraz masz już komplet: API -> Baza -> Logowanie -> Wylogowanie. 
To jest "MVP" (Minimum Viable Product) każdego systemu w firmie.
Czy w tym momencie chcesz jeszcze coś dopracować w logowaniu, czy oficjalnie zamykamy Dzień 69 i wchodzimy w pełną budowę Bloga (relacje w SQL)?






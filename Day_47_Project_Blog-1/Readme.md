Dzień 47
--------

Day_47_Project_Blog-1
---------------------

Wjeżdżamy w wielki finał. 
Projekt Bloga to moment, w którym łączysz wszystko. To jest to, co pokazujesz w portfolio na GitHubie rekruterom.
Najważniejszą rzeczą, której Angela uczy na tym etapie, są Relacje w Bazach Danych (One-to-Many).
Do tej pory Twoje tabele w bazie (użytkownicy i historia pogody) "nie wiedziały" o swoim istnieniu. 
W prawdziwym systemie Post musi mieć Autora. 
Nie wpisujesz imienia autora ręcznie jako tekst. 
Ty "łączysz" tabelę `BlogPost` z tabelą `User` za pomocą Klucza Obcego (`Foreign Key`).

Dzięki temu zmiana nazwy użytkownika automatycznie zaktualizuje się we wszystkich jego postach.

Przygotowanie:

Utwórz nowy projekt: Day_70_Blog.
Zainstaluj paczki (jeśli robisz to w nowym .venv): pip install flask flask-sqlalchemy flask-login werkzeug

Krok 1: Architektura Bazy (Plik main.py)
----------------------------------------

main.py:
Zwróć uwagę na to, jak tabele są ze sobą spięte linijkami `db.relationship`.  

```python
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-tajny-klucz-bloga'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- 1. MODELE BAZY DANYCH (RELACJE) ---

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    
    # RELACJA: Jeden użytkownik ma wiele postów. "back_populates" łączy to z polem "author" w tabeli BlogPost.
    posts = db.relationship("BlogPost", back_populates="author")

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    
    # KLUCZ OBCY (Foreign Key): Ten post należy do konkretnego ID z tabeli "users"
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # RELACJA ODWROTNA: Pozwala nam pisać np. `post.author.username` w HTML-u!
    author = db.relationship("User", back_populates="posts")

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Inicjalizacja bazy i stworzenie testowego admina
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        new_user = User(username="admin", password=generate_password_hash("haslo123"))
        db.session.add(new_user)
        db.session.commit()

# --- 2. TRASY (CRUD) ---

@app.route('/')
def get_all_posts():
    # Pobieramy wszystkie posty z bazy i przekazujemy do HTML
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('get_all_posts'))
        flash('Złe dane logowania')
    return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))

@app.route("/new-post", methods=["GET", "POST"])
@login_required # Tylko zalogowani mogą pisać posty!
def add_new_post():
    if request.method == "POST":
        new_post = BlogPost(
            title=request.form.get("title"),
            body=request.form.get("body"),
            date=datetime.now().strftime("%B %d, %Y"),
            author=current_user # MAGIA: Przypisujemy cały obiekt aktualnie zalogowanego usera!
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make_post.html")

@app.route("/post/<int:post_id>")
def show_post(post_id):
    # Pokazywanie pojedynczego posta
    requested_post = db.session.get(BlogPost, post_id)
    return render_template("post.html", post=requested_post)

if __name__ == "__main__":
    app.run(debug=True)
```

Krok 2: Szablony HTML (Frontend)
--------------------------------

Utwórz folder templates i dodaj w nim te 4 proste pliki.

1. index.html (Strona główna)

```html
<h1>Mój Blog Inżynierski</h1>
<p>
    {% if current_user.is_authenticated %}
        Zalogowany jako: {{ current_user.username }} | <a href="/logout">Wyloguj</a> | <a href="/new-post">Napisz nowy post</a>
    {% else %}
        <a href="/login">Zaloguj się</a>
    {% endif %}
</p>
<hr>
<!-- Pętla wyświetlająca posty -->
{% for post in all_posts %}
    <h2><a href="/post/{{ post.id }}">{{ post.title }}</a></h2>
    <!-- Tu widać potęgę relacji w bazie! Odwołujemy się do post.author.username -->
    <p>Napisane przez: <b>{{ post.author.username }}</b> w dniu {{ post.date }}</p>
    <hr>
{% endfor %}
```


2. post.html (Pojedynczy wpis)

```html
<a href="/">Wróć do strony głównej</a>
<h1>{{ post.title }}</h1>
<p style="color: gray;">Autor: {{ post.author.username }} | Data: {{ post.date }}</p>
<p>{{ post.body }}</p>
```

3. make_post.html (Formularz dodawania)

```html
<h1>Dodaj nowy post</h1>
<form method="POST">
    <input type="text" name="title" placeholder="Tytuł posta" required><br><br>
    <textarea name="body" rows="10" cols="50" placeholder="Treść..." required></textarea><br><br>
    <button type="submit">Opublikuj</button>
</form>
```

4. login.html (Logowanie)

```html
<h1>Logowanie</h1>
<form method="POST">
    <input type="text" name="username" placeholder="Login (admin)" required>
    <input type="password" name="password" placeholder="Hasło (haslo123)" required>
    <button type="submit">Zaloguj</button>
</form>
{% with messages = get_flashed_messages() %}
  {% if messages %} <p style="color:red;">{{ messages[0] }}</p> {% endif %}
{% endwith %}
```


Inżynieria Pod Maską (Dlaczego ten kod wymiata?):

author=current_user: 
Zwróć na to uwagę w funkcji `add_new_post`. 
Ty nie zapisujesz w bazie ID ani imienia. T
y wrzucasz do relacji CAŁY obiekt zalogowanego użytkownika (current_user z Flask-Login), 
a SQLAlchemy samo wyciąga jego ID i tworzy powiązanie w bazie.

post.author.username w HTML: 
Na stronie głównej masz pętlę przelatującą przez posty. 
Ale post nie ma w swojej tabeli kolumny "username". 
Ma tylko `author_id`. 
Dzięki relacji `db.relationship`, Jinja jest w stanie "przeskoczyć" z tabeli `BlogPost` do tabeli `User` w locie i wyciągnąć imię autora. 
To jest kwintesencja SQL.

Zmienna current_user w Jinja: 
Flask-Login automatycznie wstrzykuje obiekt `current_user` do KAŻDEGO pliku HTML. 
Możesz łatwo schować przycisk "Napisz nowy post" przed osobami, które nie są zalogowane: `{% if current_user.is_authenticated %}`.

Przetestuj to:
--------------

1. Odpal serwer. 
2. Wejdź na http://127.0.0.1:5000/. Będzie pusto. 
3. Kliknij "Zaloguj się" (wpisz admin / haslo123). 
4. Kliknij "Napisz nowy post", wymyśl tytuł i treść, opublikuj. 
5. Zobacz, jak na głównej stronie pojawia się Twój wpis z Twoim imieniem autora!

Odpal i napisz swój pierwszy post w bazie danych. 
Jak to zadziała, to masz szkielet, na którym opiera się 90% aplikacji (WordPress działa dokładnie tak samo pod spodem).


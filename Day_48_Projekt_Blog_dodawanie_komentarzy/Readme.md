Dzień 48
--------

Day_48_Projekt_Blog_dodawanie_komentarzy
----------------------------------------

Zanim wypuścisz aplikację w świat, musisz mieć pewność, że wiesz, jak łączyć dane z różnych tabel. 
To jest test ostateczny z baz danych.

Dołożenie komentarzy to tzw. Relacja Trójstronna.
Komentarz nie wisi w próżni. 
Musi wiedzieć:
1. Kto go napisał? (Klucz obcy do tabeli User)
2. Pod jakim postem? (Klucz obcy do tabeli BlogPost)

Krok 1: Twardy reset bazy danych
--------------------------------

Ponieważ dodajemy nową tabelę i nowe relacje do starych tabel, najszybszą opcją (żeby nie bawić się w skomplikowane migracje bazy) 
jest usunięcie starego pliku bazy.
Wejdź w folder instance w swoim projekcie i po prostu usuń plik `blog.db`. 
Kod sam założy nową, poprawną bazę przy starcie.

Krok 2: Nowa Architektura Bazy (main.py)
----------------------------------------

Podmień cały swój plik main.py na ten poniżej. 
Zwróć uwagę na nową klasę `Comment` i to, jak zaktualizowałem trasy (teraz `/post/<id>` przyjmuje też metodę POST, żeby zapisywać komentarze).

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

# --- 1. MODELE BAZY DANYCH (RELACJE TRÓJSTRONNE) ---

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    
    # User ma posty ORAZ komentarze
    posts = db.relationship("BlogPost", back_populates="author")
    comments = db.relationship("Comment", back_populates="comment_author")

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = db.relationship("User", back_populates="posts")
    
    # BlogPost ma wiele komentarzy pod sobą
    comments = db.relationship("Comment", back_populates="parent_post")

# NOWA TABELA: KOMENTARZE
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    
    # Kto to napisał? (Klucz do Usera)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = db.relationship("User", back_populates="comments")
    
    # Gdzie to napisał? (Klucz do Posta)
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = db.relationship("BlogPost", back_populates="comments")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        new_user = User(username="admin", password=generate_password_hash("haslo123"))
        db.session.add(new_user)
        db.session.commit()

# --- 2. TRASY ---

@app.route('/')
def get_all_posts():
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
@login_required
def add_new_post():
    if request.method == "POST":
        new_post = BlogPost(
            title=request.form.get("title"),
            body=request.form.get("body"),
            date=datetime.now().strftime("%B %d, %Y"),
            author=current_user
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make_post.html")

# AKTUALIZACJA: Dodano obsługę metody POST dla komentarzy
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.session.get(BlogPost, post_id)
    
    # Jeśli ktoś wysłał formularz komentarza
    if request.method == "POST":
        if not current_user.is_authenticated:
            flash("Musisz być zalogowany, żeby dodać komentarz.")
            return redirect(url_for("login"))
            
        new_comment = Comment(
            text=request.form.get("comment_text"),
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("show_post", post_id=post_id))
        
    return render_template("post.html", post=requested_post)

if __name__ == "__main__":
    app.run(debug=True)
```

Krok 3: Modyfikacja Frontendu (templates/post.html)
---------------------------------------------------

Teraz musimy wyświetlić te komentarze pod postem oraz dodać pole tekstowe do ich pisania.

Podmień plik `post.html` na ten kod:

```html
<a href="/">Wróć do strony głównej</a>
<hr>

<!-- 1. TREŚĆ POSTA -->
<h1>{{ post.title }}</h1>
<p style="color: gray;">Autor: {{ post.author.username }} | Data: {{ post.date }}</p>
<p style="font-size: 18px;">{{ post.body }}</p>

<hr>

<!-- 2. SEKCJA KOMENTARZY -->
<h3>Komentarze:</h3>
<ul style="list-style-type: none; padding-left: 0;">
    <!-- Magia SQL w Jinja: post.comments automatycznie wyciąga wszystkie komentarze przypięte do tego posta -->
    {% for comment in post.comments %}
        <li style="background-color: #f4f4f4; padding: 10px; margin-bottom: 10px; border-radius: 5px;">
            <p style="margin: 0;">{{ comment.text }}</p>
            <small style="color: gray;">Napisał: <b>{{ comment.comment_author.username }}</b></small>
        </li>
    {% else %}
        <p style="color: gray;">Brak komentarzy. Bądź pierwszy!</p>
    {% endfor %}
</ul>

<!-- 3. FORMULARZ DODAWANIA KOMENTARZA (Tylko dla zalogowanych) -->
{% if current_user.is_authenticated %}
    <form method="POST" style="margin-top: 20px;">
        <textarea name="comment_text" rows="3" cols="50" placeholder="Napisz komentarz..." required></textarea><br>
        <button type="submit" style="margin-top: 5px;">Dodaj komentarz</button>
    </form>
{% else %}
    <p style="color: red;">Musisz się <a href="/login">zalogować</a>, żeby dodać komentarz.</p>
{% endif %}
```

Inżynieria pod maską (Dlaczego to jest piękne):

Magia post.comments: 
Zobacz w HTML-u na pętlę: `{% for comment in post.comments %}`
Ty nie pisałeś żadnego zapytania typu `SELECT * FROM comments WHERE post_id = X`
SQLAlchemy robi to za Ciebie w tle, bo zdefiniowałeś relację `comments = db.relationship(...)` w klasie `BlogPost`. 
Wyciągasz post, a on "sam" dociąga sobie paczkę swoich komentarzy.

comment.comment_author.username: 
Tutaj przeskakujemy przez dwie tabele! 
Od Komentarza -> do Autora -> do jego Nazwy Użytkownika. 
Baza danych SQL błyskawicznie łączy (JOIN) te tabele w locie.

Zabezpieczenie na Backendzie i Frontendzie: 
Zauważ, że w HTML ukryliśmy formularz przed niezalogowanymi `{% if current_user.is_authenticated %}`. 
Ale sam Frontend to za mało (haker mógłby wysłać sztuczne żądanie POST). 
Dlatego w `main.py` też mamy warunek: `if not current_user.is_authenticated: return redirect(url_for("login"))`. 
To jest złota zasada bezpieczeństwa aplikacji.

Przetestuj to:
--------------
1. Odpal serwer (od nowa, żeby baza wygenerowała się z nową tabelą comments).
2. Zaloguj się (admin / haslo123).
3. Napisz jakiegoś posta testowego.
4. Wejdź w niego, napisz komentarz i kliknij "Dodaj".
5. Komentarz natychmiast pojawi się pod tekstem z przypisanym nickiem "admin".
6. Wyloguj się i wejdź w posta – zobaczysz komentarz, ale zamiast formularza dostaniesz komunikat "Musisz się zalogować".

Działa? Jeśli to pojąłeś, to oficjalnie znasz cykl życia aplikacji webowych od strony bazy danych, połączonych tabel i sesji użytkownika. 
Nic więcej z tzw. "Backend Web Development" na poziomie mid-developera Ci nie potrzeba.

Następny krok: 
Wyrywamy ten kod z Twojego komputera i wrzucamy na prawdziwy, publiczny serwer (Deployment na PythonAnywhere - Dzień 71). 
Wchodzimy w to?


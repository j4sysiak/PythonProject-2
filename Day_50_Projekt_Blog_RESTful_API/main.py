from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import jsonify

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

    # --- DODAJ TO do obsugi RESTFul API: ---
    # zamiana post na zwykły pythonowy słownik, który łatwo można przekształcić do JSONa
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "date": self.date,
            "author": self.author.username if self.author else "Nieznany",
            "comments_count": len(self.comments),
            # MAGIA: List Comprehension, które odpala to_dict() dla każdego komentarza przypiętego do tego posta!
            "comments":[comment.to_dict() for comment in self.comments]
        }


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

    # DODAJEMY TO, to jest  przydatne, gdybyśmy chcieli mieć endpointy REST API dla komentarzy
    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "author": self.comment_author.username if self.comment_author else "Nieznany"
        }


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


# --- REJESTRACJA NOWEGO UŻYTKOWNIKA ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username_input = request.form.get("username")
        password_input = request.form.get("password")

        # 1. Zabezpieczenie: Sprawdzamy czy taki login już istnieje w bazie
        if User.query.filter_by(username=username_input).first():
            flash("Użytkownik o takim loginie już istnieje. Zaloguj się.")
            return redirect(url_for('login'))

        # 2. Tworzymy nowego usera z zaszyfrowanym hasłem
        new_user = User(
            username=username_input,
            password=generate_password_hash(password_input, method='pbkdf2:sha256', salt_length=8)
        )
        db.session.add(new_user)
        db.session.commit()

        # 3. Od razu logujemy użytkownika po pomyślnej rejestracji
        login_user(new_user)
        return redirect(url_for('get_all_posts'))

    return render_template("register.html")

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




# ==========================================
# --- STREFA REST API (Dla innych maszyn) ---
# ==========================================

# 1. GET: Zwraca wszystkie posty w formacie JSON
@app.route('/api/posts', methods=['GET'])
def api_get_all_posts():
    posts = db.session.query(BlogPost).all()
    # Przelatujemy przez posty List Comprehension i zamieniamy każdy na słownik
    return jsonify(posts=[post.to_dict() for post in posts]), 200


# 2. GET: Zwraca jeden konkretny post po jego ID
@app.route('/api/posts/<int:post_id>', methods=['GET'])
def api_get_post(post_id):
    post = db.session.get(BlogPost, post_id)
    if post:
        return jsonify(post=post.to_dict()), 200
    else:
        return jsonify(error={"Not Found": "Taki post nie istnieje."}), 404

    # Dedykowany Endpoint dla komentarzy (Opcjonalnie, ale profesjonalnie)
    # Skoro zaktualizowaliśmy BlogPost.to_dict(), to teraz uderzając w http://127.0.0.1:5000/api/posts/1,
    # dostaniesz posta od razu z listą komentarzy w środku. To super wygodne.
    # Ale w prawdziwym REST API (jak aplikacja mobilna potrzebuje np. doczytać same komentarze na dole ekranu bez pobierania całego artykułu od nowa),
    # robi się dedykowane trasy (tzw. Sub-Routing).
# 3. GET: Zwraca TYLKO komentarze dla konkretnego posta
@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def api_get_comments(post_id):
    post = db.session.get(BlogPost, post_id)
    if post:
        # Zwracamy listę samych komentarzy
        return jsonify(comments=[comment.to_dict() for comment in post.comments]), 200
    else:
        return jsonify(error={"Not Found": "Taki post nie istnieje."}), 404

if __name__ == "__main__":
    app.run(debug=True)


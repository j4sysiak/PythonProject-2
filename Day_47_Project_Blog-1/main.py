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
    # RELACJA ODWROTNA: Pozwala nam pisać np. `post.author.username` w HTML-ie!
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
@login_required  # Tylko zalogowani mogą pisać posty!
def add_new_post():
    if request.method == "POST":
        new_post = BlogPost(
            title=request.form.get("title"),
            body=request.form.get("body"),
            date=datetime.now().strftime("%B %d, %Y"),
            author=current_user  # MAGIA: Przypisujemy cały obiekt aktualnie zalogowanego usera!
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
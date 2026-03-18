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


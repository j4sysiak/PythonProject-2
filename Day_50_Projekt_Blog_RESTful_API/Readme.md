Dzień 50
--------

Day_50_Projekt_Blog_RESTful_API
-------------------------------

Zbudowaliśmy system dla ludzi (przeglądarki, HTML, formularze). 
Teraz otwieramy go dla maszyn – budujemy RESTful API.

Po co to robimy? 
Wyobraź sobie, że Twoja firma chce wypuścić aplikację mobilną na Androida/iOS, żeby czytać Twojego bloga. 
Aplikacja mobilna nie rozumie HTML-a i CSS-a. 
Ona potrzebuje surowych danych. 
Dlatego zrobimy specjalne adresy (`endpointy`), pod którymi Twój serwer Flask nie będzie zwracał strony internetowej, 
tylko wypluje czystego JSON-a.

Krok 1: Aktualizacja Modelu BlogPost (Plik main.py)
---------------------------------------------------

Relacyjne bazy danych (SQL) i JSON to dwa różne światy. 
JSON nie rozumie obiektów SQLAlchemy. 
Musimy dorobić do klasy `BlogPost` małą metodę, która zamieni post na zwykły pythonowy słownik, 
który łatwo można przekształcić do JSONa.

Znajdź w kodzie klasę `BlogPost` i dopisz do niej metodę `to_dict`
(zwróć uwagę, jak elegancko wyciągamy imię autora z relacji!):

```python
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = db.relationship("User", back_populates="posts")
    comments = db.relationship("Comment", back_populates="parent_post")

    # --- DODAJ TO: ---
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "date": self.date,
            "author": self.author.username if self.author else "Nieznany",
            # Zliczamy ile dany post ma komentarzy
            "comments_count": len(self.comments) 
        }
```

Krok 2: Aktualizacja Modelu Comment (Plik main.py)
----------------------------------------------------

W bazach relacyjnych (SQL) powiązane dane (jak komentarze do posta) nie przesyłają się same do JSON-a. 
Musimy jawnie powiedzieć programowi, jak ma je "rozpakować".
Zrobimy to zgodnie z najlepszymi praktykami budowania API:
Nauczymy model Comment zamieniać się w słownik.
Zagnieździmy komentarze wewnątrz posta (tzw. Nested JSON).
Dodamy dedykowany endpoint dla samych komentarzy.

```python
# --- TABELA KOMENTARZY ---
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = db.relationship("User", back_populates="comments")
    
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = db.relationship("BlogPost", back_populates="comments")

    # DODAJEMY TO:
    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "author": self.comment_author.username if self.comment_author else "Nieznany"
        }
```



Krok 3: Importy i dodanie tras API (main.py)
--------------------------------------------

Na samej górze pliku upewnij się, że masz zaimportowane jsonify:

```python
from flask import jsonify
```


Teraz zjedź na sam dół pliku (tuż nad if __name__ == "__main__":) 
i wklej te dwa nowe endpointy REST API:

```python
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
```



Krok 3: Przetestuj to jak prawdziwy Inżynier
--------------------------------------------

Teraz udowodnimy, że Twój serwer ma "dwie twarze".
1. Zrestartuj serwer w PyCharmie.
2. Otwórz przeglądarkę.

Twarz nr 1 (Dla człowieka):
---------------------------
Wejdź na http://127.0.0.1:5000/. Widzisz ładną stronę HTML, przyciski, menu.

Twarz nr 2 (Dla maszyn / Aplikacji mobilnej):
---------------------------------------------
Wpisz w pasku adresu: http://127.0.0.1:5000/api/posts

BUM! Widzisz czystego JSON-a. 
Wszystkie posty, które Ty i "Jacek" stworzyliście przed chwilą przez stronę internetową, 
są teraz wystawione jako struktura danych. 
Aplikacja na telefonie może teraz wejść na ten adres, pobrać ten JSON i wyświetlić go w swojej własnej, natywnej aplikacji.

Jeśli wpiszesz http://127.0.0.1:5000/api/posts/1 
     Zobaczysz JSON-a z postem Admina. 
     Zwróć uwagę na pole "comments": [...]. 
     Będzie tam zagnieżdżony słownik z komentarzem Jacka! 
     To się nazywa Nested JSON.

Zmień adres na: http://127.0.0.1:5000/api/posts/1/comments
     Teraz dostaniesz z serwera wyłącznie strukturę komentarzy z tego posta, odciętą od całego artykułu. 
     Błyskawiczne i lekkie dla transferu danych.

Jeśli wpiszesz http://127.0.0.1:5000/api/posts/999 
     Dostaniesz elegancki błąd w formacie JSON: `{"error": {"Not Found": "Taki post nie istnieje."}}`.


Podsumowanie poziomu eksperckiego:
---------------------------------
Właśnie stworzyłeś architekturę "Headless CMS". 
Taki system jak Twój może teraz zasilać jednocześnie:
1. Stronę internetową (przez render_template).
2. Aplikację na iPhone'a (przez /api/posts).
3. Bota na Discordzie / Slacku w Twojej firmie (który np. co rano będzie odpytywał to API i wrzucał najnowszy wpis na kanał).

Działa Ci to API w przeglądarce? 
Jeśli tak, zostaje nam ostatni punkt z Twojej listy: 
Deployment (Wypuszczenie tego w świat). 
Chcesz wgrać ten system na prawdziwy serwer w internecie, żeby wyjść poza 127.0.0.1?


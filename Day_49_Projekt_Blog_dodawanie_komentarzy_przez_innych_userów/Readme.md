Dzień 49
--------

Day_49_Projekt_Blog_dodawanie_komentarzy_przez_innych_userów
------------------------------------------------------------

Skoro dodaliśmy komentarze, to żeby zobaczyć ich prawdziwą moc (relacje w bazie), musimy mieć więcej niż jednego użytkownika.
Na ten moment w Twojej bazie istnieje tylko "admin", którego stworzyliśmy na twardo w kodzie. 
Żeby "inni userzy" mogli komentować, musimy dorobić System Rejestracji (Register).
Dzięki temu wejdziesz na stronę z innej przeglądarki (albo w trybie Incognito), założysz konto np. "Jacek", wejdziesz w post napisany przez "admina" 
i zostawisz pod nim komentarz. 
Pod postem pojawią się komentarze od różnych osób.


Krok 1: Dodajemy obsługę rejestracji w main.py
----------------------------------------------

Wklej tę nową trasę (Route) gdzieś pod funkcją login(). 
Ten kod robi trzy rzeczy:
1. sprawdza czy login jest wolny
2. szyfruje hasło
3. od razu loguje nowego usera

Dodaj ten kod do main.py (Rejestracja)
Wklej to gdzieś pod funkcją `login()`:

```python
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
```

Krok 2: Stwórz plik templates/register.html
-------------------------------------------

Utwórz nowy plik w folderze templates, żeby nowy użytkownik miał gdzie wpisać login i hasło:

```html
<a href="/">Wróć do strony głównej</a>
<h1>Rejestracja</h1>
<form method="POST">
    <input type="text" name="username" placeholder="Wybierz login" required><br><br>
    <input type="password" name="password" placeholder="Wybierz hasło" required><br><br>
    <button type="submit">Zarejestruj się</button>
</form>

<!-- Wyświetlanie błędów (np. gdy login jest zajęty) -->
{% with messages = get_flashed_messages() %}
  {% if messages %} <p style="color:red;"><b>{{ messages[0] }}</b></p> {% endif %}
{% endwith %}
```

Krok 3: Zaktualizuj menu w templates/index.html
-----------------------------------------------

Zmień samą górę swojego pliku `index.html` (strony głównej), żeby niezalogowani widzieli przycisk do rejestracji:

```html
<h1>Mój Blog Inżynierski</h1>
<p>
    {% if current_user.is_authenticated %}
        Zalogowany jako: <b>{{ current_user.username }}</b> | <a href="/logout">Wyloguj</a> | <a href="/new-post">Napisz nowy post</a>
    {% else %}
        <a href="/login">Zaloguj się</a> | <a href="/register">Zarejestruj się</a>
    {% endif %}
</p>
<hr>
```

TEST INŻYNIERSKI (Zrób to dokładnie w tej kolejności):
------------------------------------------------------

Żeby zobaczyć pełną moc relacyjnych baz danych (SQL), przetestujemy to na dwóch przeglądarkach naraz, 
symulując dwóch różnych ludzi w internecie.

Przeglądarka nr 1 (np. zwykły Chrome):
1. Wejdź na http://127.0.0.1:5000/
2. Zaloguj się jako admin (hasło: haslo123).
3. Kliknij "Napisz nowy post". Wpisz tytuł: "Witam na moim nowym blogu!", dodaj jakąś treść i opublikuj.
4. Widzisz swój post na stronie głównej. Super.

Przeglądarka nr 2 (Otwórz Chrome w trybie Incognito Ctrl+Shift+N):
1. Wejdź na http://127.0.0.1:5000/. Widzisz, że nie jesteś zalogowany.
2. Kliknij Zarejestruj się.
3. Wpisz login: Jacek, wymyśl jakieś hasło i kliknij Zarejestruj.
4. Zostaniesz automatycznie zalogowany jako Jacek.
5. Kliknij w post napisany przez admina.
6. Zjedź na dół i w formularzu napisz komentarz: "Zajebisty blog, szefie!" i kliknij Dodaj komentarz.
7. Widzisz swój komentarz podpisany "Napisał: Jacek".

9. Wróć do Przeglądarki nr 1 (tej z kontem admina):
10. Odśwież stronę posta.

Zobaczysz pod swoim tekstem komentarz od Jacka!

To jest definitywny dowód, że Twoja relacyjna baza danych działa. 
Tabela Comment poprawnie połączyła się z tabelą User (Jacek) i tabelą BlogPost (Post Admina).

Wklej te kody, przeklikaj ten test i daj znać, czy Jacek skomentował posta Admina!


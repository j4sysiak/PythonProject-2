Dzień 39
--------

Day_39_Flask_Create_Server-WWW
------------------------------

Przeskakujemy do sekcji Flask. 
Zapomnij o turtle, zapomnij o przeglądarce. 
Teraz Ty stajesz się serwerem.
Flask to biblioteka, która zamienia Twój skrypt w mini-serwer WWW. 
Kiedy ktoś wejdzie pod odpowiedni adres (np. localhost:5000), Twój kod w Pythonie "odpowie" mu treścią.

Krok 1: Instalacja
------------------
W terminalu PyCharma:
`pip install flask`

Krok 2: Twój pierwszy serwer WWW
--------------------------------

```python
from flask import Flask

# 1. Tworzymy instancję aplikacji Flask
app = Flask(__name__)

# 2. Definiujemy "trasę" (Route) - czyli adres URL
@app.route("/")
def home():
    # To, co tu zwrócisz, pokaże się w przeglądarce
    return "<h1>Witaj na moim własnym serwerze!</h1><p>To działa po męsku.</p>"

# 3. Dodajemy drugą trasę
@app.route("/api/pogoda")
def pogoda():
    return {"miasto": "Berlin", "temp": 15.7}

# 4. Uruchamiamy serwer (tylko jeśli ten plik jest odpalany bezpośrednio)
if __name__ == "__main__":
    app.run(debug=True)
```

Dlaczego to jest inżynierski fundament?

@app.route("/") (Dekorator): 
To jest magia Pythona. 
Mówisz aplikacji: "Hej, kiedy ktoś wejdzie na główny adres (/), odpal tę funkcję poniżej".

debug=True: 
Jeśli zmienisz cokolwiek w kodzie, serwer automatycznie się przeładuje. 
Nie musisz go restartować ręcznie przy każdej zmianie (to oszczędza godziny pracy).

JSON jako odpowiedź: 
Zobacz funkcję `/api/pogoda`. 
Flask jest na tyle mądry, że jak zwrócisz zwykły słownik Pythona, on automatycznie zamieni go na JSON-a. 
To jest dokładnie to, co robiły API, z których korzystałeś wcześniej!

Jak to przetestować:
--------------------
Odpal main.py.

W konsoli na dole zobaczysz adres: Running on http://127.0.0.1:5000.
Kliknij w ten link (albo wpisz to w przeglądarkę).

Zobaczysz swój nagłówek. 
Dopisz `/api/pogoda` na końcu adresu w przeglądarce – zobaczysz swojego JSON-a.
`http://127.0.0.1:5000/api/pogoda`


Po co to w firmie?

Zamiast wysyłać szefowi maile z wynikami, 
możesz postawić taki mini-serwer na firmowym komputerze/serwerze. 
Twój skrypt przetwarza dane, a szef wchodzi na stronę i widzi aktualny dashboard z wynikami, bez czekania na maila.

Masz to odpalone? Działa "Witaj na moim własnym serwerze"? 
Jeśli tak, to w następnym kroku pokażę Ci, jak do tego serwera wpiąć Twojego bota pogodowego, 
żeby "serwował" pogodę w czasie rzeczywistym. Lecimy?


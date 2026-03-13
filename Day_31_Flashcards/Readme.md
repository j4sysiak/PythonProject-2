Dzień 31
--------

Day_31_Flashcards
-----------------

Capstone Project (Projekt Podsumowujący). 
Kończymy na tym etapie zabawę z interfejsami graficznymi (Tkinter).

Budujemy aplikację do nauki języków z fiszkami (Flash Card App). 
Wyświetla francuskie słówko, czeka 3 sekundy, a potem sama odwraca kartę i pokazuje tłumaczenie. 
Jak znasz słowo – klikasz zielony ptaszek (program usuwa je z listy i zapisuje postęp do pliku). 
Jak nie znasz – klikasz czerwony krzyżyk (słowo zostaje w puli).

Utwórz nowy projekt Day_31_Flashcards. 
Z materiałów kursu musisz pobrać 4 obrazki: 
 - card_front.png
 - card_back.png
 - right.png
 - wrong.png. 

Wrzuć je luzem obok pliku main.py.

Utwórz też nowy plik tekstowy, nazwij go `french_words.csv` i wklej tam te 5 linijek (żebyś miał na czym testować bez szukania plików):

```text
French,English
partie,part
histoire,history
chercher,search
seulement,only
police,police
```

Kod Dnia 31 (Czysta Inżynieria)

Wklej to do main.py. 
Zwróć uwagę na to, jak za pomocą Pandas zmieniamy tabelę w listę słowników i jak radzimy sobie ze zmianą obrazka na Płótnie w locie.

```python
import tkinter as tk
import pandas as pd
import random

BACKGROUND_COLOR = "#B1DDC6"
current_card = {}
to_learn =[]

# --- 1. WCZYTYWANIE DANYCH (Z obsługą postępu) ---
try:
    # Najpierw próbujemy wczytać plik z zapisanym postępem (słowa, których jeszcze nie znamy)
    data = pd.read_csv("words_to_learn.csv")
except FileNotFoundError:
    # Jeśli program odpala się pierwszy raz, ładujemy oryginalną bazę
    original_data = pd.read_csv("french_words.csv")
    # Zamienia tabelę na genialną strukturę:[{'French': 'partie', 'English': 'part'}, ...]
    to_learn = original_data.to_dict(orient="records")
else:
    to_learn = data.to_dict(orient="records")

# --- 2. LOGIKA LOSOWANIA I ODWRACANIA KARTY ---
def next_card():
    global current_card, flip_timer
    
    # Ubijamy stary timer, jeśli użytkownik kliknął przycisk przed upływem 3 sekund
    window.after_cancel(flip_timer)
    
    current_card = random.choice(to_learn)
    
    # Ustawiamy przednią stronę karty (Francuski)
    canvas.itemconfig(card_title, text="French", fill="black")
    canvas.itemconfig(card_word, text=current_card["French"], fill="black")
    canvas.itemconfig(card_background, image=card_front_img)
    
    # Odpalamy nowy timer, który za 3000 ms (3 sekundy) wywoła funkcję flip_card
    flip_timer = window.after(3000, func=flip_card)

def flip_card():
    # Zmieniamy obrazek i tekst na tylną stronę karty (Angielski)
    canvas.itemconfig(card_title, text="English", fill="white")
    canvas.itemconfig(card_word, text=current_card["English"], fill="white")
    canvas.itemconfig(card_background, image=card_back_img)

# --- 3. ZAPISYWANIE POSTĘPU ---
def is_known():
    # Usuwamy aktualną kartę z listy
    to_learn.remove(current_card)
    
    # Zapisujemy nową, krótszą listę do pliku z postępem (bez indeksów po lewej stronie tabeli)
    data = pd.DataFrame(to_learn)
    data.to_csv("words_to_learn.csv", index=False)
    
    # Losujemy kolejną kartę
    next_card()

# --- 4. INTERFEJS GRAFICZNY (GUI) ---
window = tk.Tk()
window.title("Flashy")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)

# Od razu inicjujemy pusty timer, żeby w next_card() było co ubijać
flip_timer = window.after(3000, func=flip_card)

# Płótno (Canvas)
canvas = tk.Canvas(width=800, height=526)
card_front_img = tk.PhotoImage(file="card_front.png")
card_back_img = tk.PhotoImage(file="card_back.png")
# Tworzymy obrazek na środku płótna (400x263) i przypisujemy mu zmienną, żeby móc go potem podmieniać
card_background = canvas.create_image(400, 263, image=card_front_img)
card_title = canvas.create_text(400, 150, text="", font=("Arial", 40, "italic"))
card_word = canvas.create_text(400, 263, text="", font=("Arial", 60, "bold"))
canvas.config(bg=BACKGROUND_COLOR, highlightthickness=0)
canvas.grid(row=0, column=0, columnspan=2)

# Przyciski
cross_image = tk.PhotoImage(file="wrong.png")
unknown_button = tk.Button(image=cross_image, highlightthickness=0, command=next_card)
unknown_button.grid(row=1, column=0)

check_image = tk.PhotoImage(file="right.png")
known_button = tk.Button(image=check_image, highlightthickness=0, command=is_known)
known_button.grid(row=1, column=1)

# Losujemy pierwszą kartę na start programu
next_card()

window.mainloop()
```

Co jest tu kluczowe (Inżynieria pod maską):
-------------------------------------------

`window.after_cancel(flip_timer)`: 
To jest łatka na błąd, który popełnia 90% początkujących. 
Gdybyś tego nie dodał, a użytkownik w 2 sekundy przeklikałby 5 kart w amoku, program odpaliłby 5 różnych timerów w tle. 
Nagle karty zaczęłyby się same odwracać z prędkością karabinu maszynowego. 
My przed wylosowaniem nowej karty ZAWSZE ubijamy stary odliczający zegar.

`Dynamiczna zmiana obrazka`: 
Podobnie jak z tekstem w Pomodoro, żeby podmienić grafikę na Canvas, używasz: `canvas.itemconfig(card_background, image=card_back_img)`.

`index=False w to_csv()`: 
Jeśli tego nie dopiszesz, Pandas przy każdym zapisie dodaje po lewej stronie kolumnę z numerami 0, 1, 2, 3... 
Kiedy wczytasz to ponownie, program się wykrzaczy. 
To małe ustawienie jest obowiązkowe przy nadpisywaniu plików z danymi.

`to_dict(orient="records")`: 
To jest trik z Pandas, za który kiedyś mi podziękujesz. 
Domyślnie Pandas czyta tabele w dziwny słownik kolumn. 
Ten parametr tnie tabelę na wiersze i zwraca klasyczną listę słowników (np. [{"French": "pies", "English": "dog"}, ...]). 
Pętle po czymś takim to w Pythonie czysta przyjemność.

glębsze wyjaśnienie:  to_dict()
-------------------------------

Wyjaśnię Ci to na konkretnym przykładzie, bo to jedna z najważniejszych rzeczy przy pracy z danymi w Pythonie.

Wyobraź sobie nasz plik CSV z fiszkami. Wygląda tak:

```csv
French,English
partie,part
histoire,history
```

Kiedy wczytasz to przez Pandas (pd.read_csv), program ładuje to do pamięci jako tabelę. 
Ale żeby w Pythonie łatwo losować karty, potrzebujemy zamienić tę tabelę na standardowy słownik (komenda to_dict()).

I tu pojawia się problem z domyślnym zachowaniem biblioteki Pandas.

1. Domyślne zachowanie (Zwykłe data.to_dict())

Jeśli nie wpiszesz w nawiasie niczego, Pandas potnie tę tabelę PIONOWO (kolumnami). Wypluje Ci taki potworek:

```json
Python
{
    'French': {0: 'partie', 1: 'histoire'}, 
    'English': {0: 'part', 1: 'history'}
}
```

Dlaczego to jest "dziwne" i złe dla nas?
Bo rozerwało nam fiszki na pół! 
Słowo francuskie i jego angielskie tłumaczenie leżą w zupełnie innych miejscach. 
Żeby wylosować jedną kartę, musiałbyś wylosować numer (np. 0), a potem pisać skomplikowany kod, 
żeby wyciągnąć French[0] i połączyć z English[0]. Kompletny syf.

2. Podejście inżynieryjne: `data.to_dict(orient="records")`

Parametr orient="records" mówi do Pandas: "Słuchaj, nie tnij tego pionowo. 
Potnij to POZIOMO, wiersz po wierszu (rekord po rekordzie), i spakuj do jednej listy".

Wynik wygląda tak:

```json
Python[
    {'French': 'partie', 'English': 'part'}, 
    {'French': 'histoire', 'English': 'history'}
]
```
 

Dlaczego to jest genialne?
Bo teraz masz Listę, w której każdy element to jedna kompletna fiszka.

Dzięki temu w kodzie mogliśmy po prostu użyć wbudowanej funkcji losującej z listy:

```python
current_card = random.choice(to_learn)
```


Python sam losuje jeden cały wiersz (np. ten z indeksem 1). 
I od tego momentu w zmiennej `current_card` masz elegancki pakiet: `{'French': 'histoire', 'English': 'history'}`.

Chcesz wyświetlić francuskie słowo? 
Piszesz current_card["French"]. 

Chcesz angielskie? 
Piszesz current_card["English"].

Podsumowując:
W analizie danych (jak liczysz średnie zarobki w kolumnie), domyślne cięcie pionowe ma sens. 
Ale kiedy robisz aplikację/grę i każda linijka w Excelu to osobny obiekt (fiszka, użytkownik, samochód), ZAWSZE używasz orient="records".

 



Odpal program. 
Wyświetli się biała karta z francuskim słowem. 
Poczekaj 3 sekundy – odwróci się na zieloną stronę z angielskim. 
Kliknij zielony ptaszek – słowo zniknie z puli, a w Twoim projekcie wygeneruje się plik words_to_learn.csv.


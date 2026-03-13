import tkinter as tk
import pandas as pd
import random

BACKGROUND_COLOR = "#B1DDC6"
current_card = {}
to_learn = []


# --- 1. WCZYTYWANIE DANYCH (Kuloodporne) ---
try:
    # Najpierw próbujemy wczytać plik z zapisanym postępem (słowa, których jeszcze nie znamy)
    data = pd.read_csv("words_to_learn.csv")
# Łapiemy DWA błędy naraz: brak pliku LUB plik jest pusty
except (FileNotFoundError, pd.errors.EmptyDataError):
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

    # ZABEZPIECZENIE: Sprawdzamy, czy zostały jeszcze jakieś słówka
    if len(to_learn) == 0:
        canvas.itemconfig(card_title, text="Gratulacje!", fill="black")
        canvas.itemconfig(card_word, text="Znasz już wszystkie słowa.", fill="black")
        canvas.itemconfig(card_background, image=card_front_img)
        # Wyłączamy przyciski (blokujemy możliwość klikania)
        known_button.config(state="disabled")
        unknown_button.config(state="disabled")
        return # Przerywamy dalsze działanie funkcji

    current_card = random.choice(to_learn)

    # Ustawiamy przednią stronę karty (Francuski)
    canvas.itemconfig(card_title, text="French", fill="black")
    canvas.itemconfig(card_word, text=current_card["French"], fill="black")
    canvas.itemconfig(card_background, image=card_front_img)

    # Odpalamy nowy timer, który za 3000 ms (3 sekundy) wywoła funkcję flip_card
    flip_timer = window.after(3000, func=flip_card) # # Zmieniamy obrazek i tekst na tylną stronę karty (Angielski)


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
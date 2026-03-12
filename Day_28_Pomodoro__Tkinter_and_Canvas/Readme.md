Dzień 28
--------

Dzień 28: Aplikacja Pomodoro (Zarządzanie czasem w GUI)
-------------------------------------------------------

Ten projekt to przełom w rozumieniu interfejsów graficznych. 
Uczysz się tutaj najważniejszej zasady aplikacji okienkowych: `Nigdy nie używaj time.sleep() w GUI`.
Dlaczego? Bo time.sleep() usypia cały program. Okienko by zamarzło, system wyrzuciłby komunikat "Brak odpowiedzi", 
a Ty nie mógłbyś nawet kliknąć przycisku "Zamknij".

Zamiast tego użyjemy wbudowanej w `Tkinter` metody `window.after()`, 
która mówi systemowi: "Zrób to za X milisekund, a w międzyczasie normalnie reaguj na kliknięcia".

Pobierz tylko jeden plik: tomato.png. Wrzuć go luzem do folderu z projektem, obok pliku main.py.

Oto czysty, inżynieryjny kod. Skopiuj i wklej do main.py:

```python
import tkinter as tk
import math

# --- STAŁE (Konfiguracja w jednym miejscu - standard branżowy) ---
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20

# Zmienne globalne do kontrolowania stanu aplikacji
reps = 0
timer = None

# --- LOGIKA TIMERA ---
def reset_timer():
    global reps
    window.after_cancel(timer) # Ubija aktualnie odliczający proces
    canvas.itemconfig(timer_text, text="00:00")
    title_label.config(text="Timer", fg=GREEN)
    check_marks.config(text="")
    reps = 0

def start_timer():
    global reps
    reps += 1
    
    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BREAK_MIN * 60

    # Decydujemy, co teraz: praca, krótka przerwa czy długa przerwa (co 8 cykl)
    if reps % 8 == 0:
        count_down(long_break_sec)
        title_label.config(text="Break", fg=RED)
    elif reps % 2 == 0:
        count_down(short_break_sec)
        title_label.config(text="Break", fg=PINK)
    else:
        count_down(work_sec)
        title_label.config(text="Work", fg=GREEN)

def count_down(count):
    global timer
    # Matematyka: wyciągamy minuty i resztę sekund z całkowitego czasu
    count_min = math.floor(count / 60)
    count_sec = count % 60

    # Dynamiczne formatowanie tekstu (np. żeby zamiast "5:0" wyświetlało "05:00")
    if count_sec < 10:
        count_sec = f"0{count_sec}"

    # Zmiana tekstu na obiekcie Canvas
    canvas.itemconfig(timer_text, text=f"{count_min}:{count_sec}")

    if count > 0:
        # Tu dzieje się magia: odpal tę samą funkcję za 1000ms (1 sekunda), przekazując czas - 1
        timer = window.after(1000, count_down, count - 1)
    else:
        # Gdy czas zjedzie do zera, automatycznie odpal kolejny cykl
        start_timer()
        # Dodawanie "ptaszków" za ukończone sesje pracy
        marks = ""
        work_sessions = math.floor(reps/2)
        for _ in range(work_sessions):
            marks += "✔"
        check_marks.config(text=marks)

# --- INTERFEJS GRAFICZNY (GUI) ---
window = tk.Tk()
window.title("Pomodoro")
window.config(padx=100, pady=50, bg=YELLOW)

# Label tytułowy
title_label = tk.Label(text="Timer", fg=GREEN, bg=YELLOW, font=(FONT_NAME, 50))
title_label.grid(column=1, row=0)

# Canvas (Płótno) - pozwala nakładać tekst na obrazki
canvas = tk.Canvas(width=200, height=224, bg=YELLOW, highlightthickness=0)
tomato_img = tk.PhotoImage(file="tomato.png")
canvas.create_image(100, 112, image=tomato_img) # Współrzędne X,Y środka płótna
timer_text = canvas.create_text(100, 130, text="00:00", fill="white", font=(FONT_NAME, 35, "bold"))
canvas.grid(column=1, row=1)

# Przyciski
start_button = tk.Button(text="Start", highlightthickness=0, command=start_timer)
start_button.grid(column=0, row=2)

reset_button = tk.Button(text="Reset", highlightthickness=0, command=reset_timer)
reset_button.grid(column=2, row=2)

# Znaczniki postępu (ptaszki)
check_marks = tk.Label(fg=GREEN, bg=YELLOW, font=(FONT_NAME, 20))
check_marks.grid(column=1, row=3)

window.mainloop()
```

Co tu jest najważniejsze (Inżynieria pod maską):

Metoda Canvas (Płótno): 
`Tkinter` domyślnie układa elementy w siatce (grid), jeden obok drugiego. 
Jak chcesz mieć tekst NA obrazku (jak czas na pomidorze), musisz użyć `Canvas`. 
Tylko płótno pozwala na takie warstwowanie (jak w Photoshopie).

window.after(1000, count_down, count - 1): 
To asynchroniczne wywołanie. 
Zamiast pętli while, funkcja wywołuje samą siebie z opóźnieniem 1 sekundy (1000 ms). 
Twoje okno działa płynnie, przyciski klikają się bez lagów, a czas leci w tle.

Zmienna global timer: 
Kiedy klikasz "Reset", musimy ubić pętlę odliczającą, żeby czas nie zwariował. 
Dlatego wynik metody after() przypisujemy do globalnej zmiennej timer, żeby potem w funkcji reset_timer() użyć brutalnego `window.after_cancel(timer)`.

Słowo kluczowe global: 
Domyślnie funkcja w Pythonie nie może nadpisywać zmiennej, która została stworzona poza nią. 
Jak napiszesz `global reps`, dajesz funkcji uprawnienia do modyfikacji tej głównej zmiennej.

Pobierz obrazek, odpal skrypt. Kliknij Start i zobacz jak to elegancko odlicza czas.

trochę teorii, ale to jest właśnie ten moment, kiedy zaczynasz rozumieć, jak działają aplikacje okienkowe.
----------------------------------------------------------------------------------------------------------

Główny problem, z którym zderzają się tu początkujący: 
jak zrobić odliczanie czasu? 

Pierwsza myśl to pętla while i time.sleep(1). 

W aplikacjach okienkowych to samobójstwo. sleep() usypia cały wątek programu – okno zamarza, system myśli, że program się zawiesił (słynne "Brak odpowiedzi") i nie możesz nawet kliknąć przycisku Stop.
Rozwiązaniem jest asynchroniczna metoda .after(), która mówi systemowi: "Zrób to za sekundę, a w międzyczasie normalnie reaguj na myszkę i klawiaturę".

Co jest najważniejsze z perspektywy programisty:
Widżet Canvas: 
W Dniu 27 używaliśmy Label do wyświetlania wszystkiego. 
Tutaj wjeżdża Płótno (Canvas).
W Tkinterze nie da się tak po prostu nałożyć tekstu na zwykły obrazek w sposób kontrolowany. 
Płótno zachowuje się jak obszar roboczy w Photoshopie – kładziesz obrazek na warstwie pierwszej, a tekst na warstwie drugiej (create_image, create_text).

canvas.itemconfig(): 
Zwróć na to uwagę w funkcji count_down. 
Skoro tekst z czasem znajduje się na Płótnie, to nie zmienisz go komendą `.config()`. 
Musisz użyć `.itemconfig(`)`, podać ID tego konkretnego tekstu (timer_text) i dopiero wtedy wrzucić nową wartość.

Rekurencja i Zmienne Globalne: 
Słowo kluczowe `global timer` pozwala funkcji modyfikować zmienną, która żyje w głównej pamięci programu. 
Gdyby nie to, po kliknięciu "Reset" program nie wiedziałby, który proces ma ubić, bo każda funkcja tworzyłaby swoją lokalną kopię zmiennej.


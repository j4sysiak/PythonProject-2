import tkinter as tk
import math

# Zasada w Pythonie: global x
# | Operacja                             | Czy potrzebne global? |
# |--------------------------------------|-----------------------|
# | Odczyt zmiennej globalnej            | ❌ Nie                |
# | Zapis/modyfikacja zmiennej globalnej | ✅ Tak                |

# --- STAŁE (Konfiguracja w jednym miejscu - standard branżowy) ---
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 3
SHORT_BREAK_MIN = 1
LONG_BREAK_MIN = 2

# Zmienne globalne do śledzenia stanu
# Na poziomie modułu (poza jakąkolwiek funkcją) każda zmienna jest automatycznie globalna.
# Słowo global nie jest tu potrzebne ani dozwolone w tym kontekście.
# Poziom modułu — automatycznie globalna
reps = 0
timer = None
timer = None


# --- LOGIKA TIMERA ---
def reset_timer():
    # używa global reps, bo resetuje wartość (reps = 0).
    global reps
    window.after_cancel(timer)  # Ubija aktualnie odliczający proces
    canvas.itemconfig(timer_text, text="00:00")
    title_label.config(text="Timer", fg=GREEN)
    check_marks.config(text="")
    reps = 0  # ← "global, bo tu chcę MODYFIKOWAĆ tą globalną zmienną w tej funkcji"


def start_timer():
    # Słowo global reps w linii 31 jest potrzebne tylko dlatego, że funkcja start_timer() modyfikuje tę zmienną (reps += 1).
    # Bez global Python potraktowałby reps jako zmienną lokalną funkcji i rzuciłby błąd UnboundLocalError.
    # deklaracja dostępu do zmiennej globalnej wewnątrz funkcji jest potrzebna tylko wtedy, gdy chcesz ją modyfikować (np. przypisać nową wartość).
    #              ←  Słowo global mówi: „nie twórz nowej — użyj tej z poziomu modułu".
    global reps  # ← "global, bo chcę MODYFIKOWAĆ tę globalną zmienną gdzieś w tej funkcji"
    reps += 1    # ← "global, bo tu chcę MODYFIKOWAĆ tą globalną zmienną w tej funkcji"

    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BREAK_MIN * 60

    # Decydujemy, co teraz: praca, krótka przerwa czy długa przerwa (co 8. powtórzenie = po 4 sesjach pracy)
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
    global timer  # ← "global, bo chcę MODYFIKOWAĆ tę globalną zmienną gdzieś w tej funkcji"
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
        timer = window.after(1000, count_down, count - 1)  # ← "global, bo tu chcę MODYFIKOWAĆ tą globalną zmienną w tej funkcji"
    else:
        # Gdy czas zjedzie do zera, automatycznie odpal kolejny cykl
        start_timer()
        # Dodawanie "ptaszków" za ukończone sesje pracy
        marks = ""
        work_sessions = math.floor(reps / 2)
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
canvas.create_image(100, 112, image=tomato_img)  # Współrzędne X,Y środka płótna
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
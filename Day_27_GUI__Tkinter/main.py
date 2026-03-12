import tkinter as tk

# 1. Tworzymy silnik głównego okna
window = tk.Tk()
window.title("Mile to Km Converter")
# Ustawiamy minimalny rozmiar okna i marginesy (padx/pady), żeby elementy nie dotykały krawędzi
window.minsize(width=300, height=150)
window.config(padx=20, pady=20)

# 2. Funkcja wykonawcza (Event Handler)
def calculateFunc():
    # .get() wyciąga to, co wpisałeś w polu tekstowym (jako String)
    miles = float(input_field.get())
    km = round(miles * 1.60934, 2)
    # .config() to metoda, którą nadpisujesz parametry już istniejącego obiektu
    result_label.config(text=f"{km}")

# 3. Widget: Pole wprowadzania (Entry)
input_field = tk.Entry(width=10)
input_field.insert(tk.END, string="0") # Wrzuca domyślne 0 na start
input_field.grid(column=1, row=0) # Umieszczamy widget w siatce (grid) na kolumnie 1, wierszu 0

# 4. Widgety: Teksty (Labels)
miles_label = tk.Label(text="Miles", font=("Arial", 12))
miles_label.grid(column=2, row=0)

is_equal_label = tk.Label(text="is equal to", font=("Arial", 12))
is_equal_label.grid(column=0, row=1)

# To jest Label, w którym będzie pojawiał się wynik. Zaczyna od "0".
result_label = tk.Label(text="0", font=("Arial", 12, "bold"))
result_label.grid(column=1, row=1)

km_label = tk.Label(text="Km", font=("Arial", 12))
km_label.grid(column=2, row=1)

# 5. Widget: Przycisk (Button)
# Przekazujemy NAZWĘ funkcji do 'command'. Bez nawiasów ()!
calculate_button = tk.Button(text="Calculate", command=calculateFunc)
calculate_button.grid(column=1, row=2)

# 6. Główna pętla programu (Musi być na samym końcu)
window.mainloop()
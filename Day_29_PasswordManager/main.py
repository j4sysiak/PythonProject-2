import tkinter as tk
from tkinter import messagebox  # Pop-upy trzeba importować osobno!
import random
import pyperclip


# --- 1. GENERATOR HASEŁ ---
def generate_password():
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    numbers = '0123456789'
    symbols = '!#$%&()*+'

    # Losujemy po kilka znaków z każdej puli (tzw. List Comprehension w akcji)

    # Rozbijmy ją na części list comprehension, żeby było jasne, co się dzieje:
    # random.randint(8, 10) — losuje liczbę całkowitą z zakresu 8–10 (włącznie), czyli ile liter ma się pojawić w haśle.
    # range(...) — tworzy zakres iteracji (np. 8, 9 lub 10 razy).
    # random.choice(letters) — losuje jedną literę ze stringa letters (małe i wielkie litery a–z).
    # for _ in range(...) — pętla powtarzająca losowanie tyle razy, ile wylosował randint. Zmienna _ oznacza, że indeks iteracji nie jest nam potrzebny.
    # [...] — całość to list comprehension, czyli skrócony zapis tworzenia listy w jednej linii.

    password_letters = [random.choice(letters) for _ in range(random.randint(8, 10))]
    password_symbols = [random.choice(symbols) for _ in range(random.randint(2, 4))]
    password_numbers = [random.choice(numbers) for _ in range(random.randint(2, 4))]

    # Łączymy wszystko w jedną listę i mieszamy
    password_list = password_letters + password_symbols + password_numbers
    random.shuffle(password_list)

    # Zlepiamy listę w jeden string
    password = "".join(password_list)

    # Czyszczenie pola i wklejanie nowego hasła
    # password_entry.delete(0, tk.END)
    # password_entry.insert(0, password)
    # --- TE TRZY LINIE SĄ KLUCZOWE ---
    # bo pole password musi byc READ ONLY, więc nie możemy go czyścić normalnie, ale musimy najpierw odblokować,
    # potem wyczyścić, wkleic nowe hasło, a na końcu zablokować z powrotem.
    password_entry.config(state="normal")      # 1. Otwieramy kłódkę (pozwalamy programowi pisać)
    password_entry.delete(0, tk.END)           # 2. Czyścimy stare śmieci
    password_entry.insert(0, password)         # 3. Wklejamy nowe hasło
    password_entry.config(state="readonly")    # 4. Zamykamy kłódkę (blokujemy usera)

    # Magia: automatycznie kopiuje hasło do schowka Windowsa (Ctrl+C)
    pyperclip.copy(password)


# --- 2. ZAPISYWANIE HASŁA DO PLIKU ---
def save():
    website = website_entry.get()
    email = email_entry.get()
    password = password_entry.get()

    # Zabezpieczenie przed pustymi polami
    if len(website) == 0 or len(password) == 0:
        messagebox.showinfo(title="Oops", message="Please don't leave any fields empty!")
    else:
        # Pytamy użytkownika, czy na pewno chce zapisać
        is_ok = messagebox.askokcancel(title=website, message=f"These are the details entered: \nEmail: {email} "
                                                              f"\nPassword: {password} \nIs it ok to save?")
        if is_ok:
            # Używamy bloku "with", żeby plik zamknął się automatycznie. Tryb "a" (append) dopisuje na końcu.
            with open("data.txt", "a") as data_file:
                data_file.write(f"{website} | {email} | {password}\n")

            # Czyścimy pola po zapisaniu (od indeksu 0 do końca)
            # website_entry.delete(0, tk.END)
            # password_entry.delete(0, tk.END)
            # --- TU JEST KLUCZOWE: ODBLOKOWANIE, CZYSZCZENIE, ZABLOKOWANIE ---
            # bo pole password musi byc READ ONLY, więc nie możemy go czyścić normalnie, ale musimy najpierw odblokować, potem wyczyścić,
            # a na końcu zablokować z powrotem.
            # Pole website jest normalne, więc czyścimy je normalnie.
            website_entry.delete(0, tk.END)  # To nie jest zablokowane, więc czyścimy normalnie

            password_entry.config(state="normal")  # 1. Otwieramy kłódkę
            password_entry.delete(0, tk.END)  # 2. Czyścimy
            password_entry.config(state="readonly")  # 3. Zamykamy kłódkę


# --- 3. INTERFEJS GRAFICZNY (GUI) ---
window = tk.Tk()
window.title("Password Manager")
window.config(padx=50, pady=50)

# Płótno na logo (Canvas)
canvas = tk.Canvas(height=200, width=200)
logo_img = tk.PhotoImage(file="logo.png")
canvas.create_image(100, 100, image=logo_img)
canvas.grid(row=0, column=1)

# Etykiety (Labels)
website_label = tk.Label(text="Website:")
website_label.grid(row=1, column=0)
email_label = tk.Label(text="Email/Username:")
email_label.grid(row=2, column=0)
password_label = tk.Label(text="Password:")
password_label.grid(row=3, column=0)

# Pola tekstowe (Entries)
website_entry = tk.Entry(width=35)
website_entry.grid(row=1, column=1, columnspan=2)
website_entry.focus()  # Od razu ustawia kursor w tym polu po uruchomieniu apki

email_entry = tk.Entry(width=35)
email_entry.grid(row=2, column=1, columnspan=2)
email_entry.insert(0, "twoj.email@gmail.com")  # Domyślny email, żeby nie wpisywać go 100 razy

password_entry = tk.Entry(width=17)
password_entry.grid(row=3, column=1)
# DODAJ TO - bo pole password musi byc READ ONLY:
password_entry.config(state="readonly")

# Przyciski (Buttons)
generate_password_button = tk.Button(text="Generate Password", width=14, command=generate_password)
generate_password_button.grid(row=3, column=2)

add_button = tk.Button(text="Add", width=36, command=save)
add_button.grid(row=4, column=1, columnspan=2)

window.mainloop()
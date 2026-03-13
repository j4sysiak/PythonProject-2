import tkinter as tk
from tkinter import messagebox  # Pop-upy trzeba importować osobno!
import random
import pyperclip
import json


# --- 1. GENERATOR HASEŁ ---
def generate_password():
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    numbers = '0123456789'
    symbols = '!#$%&()*+'

    # Losujemy po kilka znaków z każdej puli (tzw. List Comprehension w akcji)

    # Co robi: "list comprehension" ?
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


# --- WYSZUKIWANIE HASŁA ---
def find_password():
    website = website_entry.get()

    # Próbujemy otworzyć plik JSON
    try:
        with open("data.json", "r") as data_file:
            # Wczytanie danych z JSONa do pythonowego słownika
            data = json.load(data_file)  # data — to będzie słownik wczytany z pliku data.json

    # Jeśli plik jeszcze nie istnieje (FileNotFoundError), rzucamy pop-up
    except FileNotFoundError:
        messagebox.showinfo(title="Error", message="No Data File Found.")

    # Jeśli plik się otworzył bez błędu (czyli try przeszło pomyślnie):
    else:
        # Sprawdzamy, czy wpisana strona istnieje w naszym słowniku
        if website in data:
            # kroki:
            # 1. data[website] — pobiera wewnętrzny słownik dla danej strony
            #                    (np. data["Facebook"] zwróci {"email": "twoj.email@gmail.com", "password": "abc123"}).
            # 2. data[website]["email"] — z tego wewnętrznego słownika wyciąga wartość pod kluczem "email", np. "twoj.email@gmail.com".
            email = data[website]["email"]

            password = data[website]["password"]
            messagebox.showinfo(title=website, message=f"Email: {email}\nPassword: {password}")
        else:
            messagebox.showinfo(title="Error", message=f"No details for {website} exists.")


# --- ZAPISYWANIE HASŁA DO JSON ---
def save():
    website = website_entry.get()
    email = email_entry.get()
    password = password_entry.get()

    # Tworzymy strukturę słownika, jakiej wymaga JSON
    # zmienan typu: dict (słownik Pythona)
    new_data = {
        website: {
            "email": email,
            "password": password
        }
    }

    if len(website) == 0 or len(password) == 0:
        messagebox.showinfo(title="Oops", message="Please don't leave any fields empty!")
    else:
        # Próbujemy otworzyć stary plik i pobrać dane
        try:
            with open("data.json", "r") as data_file:
                # 1. Czytamy stare dane
                data = json.load(data_file)  # zmienan typu: dict (słownik Pythona)

        # Jeśli plik nie istnieje, to blok 'except' stworzy nowy plik i wrzuci tam 'new_data'
        except FileNotFoundError:
            with open("data.json", "w") as data_file:
                json.dump(new_data, data_file, indent=4)

        # Jeśli plik istniał, blok 'else' aktualizuje pobrane dane i nadpisuje plik
        else:
            # 2. Aktualizujemy słownik o nowy wpis
            data.update(new_data)
            with open("data.json", "w") as data_file:
                # 3. Zapisujemy zaktualizowany słownik z powrotem do pliku
                json.dump(data, data_file, indent=4)

        # Blok 'finally' wykona się ZAWSZE, niezależnie od tego czy był błąd, czy nie
        finally:
            website_entry.delete(0, tk.END)

            # Odblokowanie, czyszczenie i zablokowanie kłódki na hasło
            password_entry.config(state="normal")
            password_entry.delete(0, tk.END)
            password_entry.config(state="readonly")


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
website_entry = tk.Entry(width=17)
website_entry.grid(row=1, column=1)
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

search_button = tk.Button(text="Search", width=14, command=find_password)
search_button.grid(row=1, column=2)

window.mainloop()
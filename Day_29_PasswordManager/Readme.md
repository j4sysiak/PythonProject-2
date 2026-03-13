Dzień 29
--------

Day_29_PasswordManager
----------------------

Łączymy tu wszystko, czego się do tej pory nauczyłeś: 
1. GUI (Tkinter)
2. operacje na plikach (zapis do .txt)
3. logika (generator trudnych haseł).

Pobierz z materiałów kursu plik logo.png (obrazek z kłódką) i wrzuć go obok pliku main.py.

Ten projekt używa genialnej paczki do automatycznego kopiowania tekstu do schowka systemu Windows. 
Otwórz terminal w PyCharmie (upewnij się, że masz (.venv)) i wpisz po męsku:
`pip install pyperclip`



Wklej to do pliku main.py. 
Zwróć uwagę na ułożenie elementów w siatce (grid) i wyskakujące okienka (messagebox).

```python
import tkinter as tk
from tkinter import messagebox # Pop-upy trzeba importować osobno!
import random
import pyperclip

# --- 1. GENERATOR HASEŁ ---
def generate_password():
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    numbers = '0123456789'
    symbols = '!#$%&()*+'

    # Losujemy po kilka znaków z każdej puli (tzw. List Comprehension w akcji)
    password_letters =[random.choice(letters) for _ in range(random.randint(8, 10))]
    password_symbols =[random.choice(symbols) for _ in range(random.randint(2, 4))]
    password_numbers = [random.choice(numbers) for _ in range(random.randint(2, 4))]

    # Łączymy wszystko w jedną listę i mieszamy
    password_list = password_letters + password_symbols + password_numbers
    random.shuffle(password_list)

    # Zlepiamy listę w jeden string
    password = "".join(password_list)

    # Czyszczenie pola i wklejanie nowego hasła
    password_entry.delete(0, tk.END)
    password_entry.insert(0, password)
    
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
            website_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)

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
website_entry.focus() # Od razu ustawia kursor w tym polu po uruchomieniu apki

email_entry = tk.Entry(width=35)
email_entry.grid(row=2, column=1, columnspan=2)
email_entry.insert(0, "twoj.email@gmail.com") # Domyślny email, żeby nie wpisywać go 100 razy

password_entry = tk.Entry(width=17)
password_entry.grid(row=3, column=1)

# Przyciski (Buttons)
generate_password_button = tk.Button(text="Generate Password", width=14, command=generate_password)
generate_password_button.grid(row=3, column=2)

add_button = tk.Button(text="Add", width=36, command=save)
add_button.grid(row=4, column=1, columnspan=2)

window.mainloop()
```

Co tu jest najważniejsze (Inżynieria pod maską):

messagebox (Pop-upy): 
To nie jest domyślnie ładowane z import `tkinter as tk`. 
Musisz to zaimportować osobno (from `tkinter import messagebox`). 
Używamy tu `showinfo` do rzucenia błędu i `askokcancel` do wygenerowania okienka z przyciskami OK/Anuluj (które zwraca wartość True/False).

columnspan=2: 
W końcu używamy pełnej mocy siatki (grid). 
Pole na stronę internetową (website_entry) jest długie. 
Mówimy mu: "Zajmij swoją kolumnę nr 1 ORAZ wjedź na kolumnę nr 2". 
Dzięki temu przycisk "Generate Password" pod spodem ładnie mieści się w tej drugiej kolumnie.

Cykl życia formularza: 
Profesjonalne aplikacje pomagają użytkownikowi. 
Dlatego daliśmy `website_entry.focus()` (kursor od razu miga w pierwszym polu), 
uzupełniliśmy e-mail domyślnie przez `.insert()` i po udanym zapisie czyścimy pola wpisywania używając `.delete(0, tk.END)`.

Paczka pyperclip: 
Klikasz "Generate Password" i... nic nie musisz zaznaczać. 
Hasło jest od razu w schowku Twojego systemu. 
Możesz od razu wcisnąć Ctrl + V w przeglądarce. 
Mała rzecz, a robi z Twojego skryptu profesjonalne narzędzie.

Zadanie dla Ciebie:
Odpal to. Wpisz "Facebook", kliknij "Generate Password", a potem "Add". 
Pojawi się okienko potwierdzenia. 
Jak klikniesz OK, po lewej stronie w PyCharmie pojawi się nowy plik data.txt z Twoimi zapisanymi danymi.

Daj znać, czy ten menadżer śmiga. 
W Dniu 30 Angela pokazuje, co się stanie, gdy użytkownik zrobi coś głupiego (np. skasuje plik data.txt) 
        – wchodzimy w temat obsługi wyjątków (try / except / finally). 

Uodparniamy aplikację na wysypywanie się. Gotowy?


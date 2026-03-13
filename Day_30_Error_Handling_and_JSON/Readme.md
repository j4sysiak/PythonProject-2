Dzień 30
--------

Day_30_Error_Handling_and_JSON
------------------------------

To jest ten moment, kiedy Twój kod przestaje być zabawką, która wywala się przy najmniejszym błędzie użytkownika,
a staje się stabilnym, "idiotoodpornym" oprogramowaniem.

Zrobimy dwie kluczowe rzeczy:
1. Zmieniamy `data.txt` na `data.json`. 
   JSON to format, który pod maską wygląda dokładnie jak słownik w Pythonie (klucz: wartość). 
   Dzięki temu łatwo z niego wyciągać konkretne dane, zamiast ciąć zwykły tekst.

2. Dodajemy blok `try / except`. 
   Co się stanie, jak program spróbuje otworzyć plik `data.json`, żeby coś w nim znaleźć, a ten plik jeszcze nie istnieje (bo to pierwsze uruchomienie)? 
   Normalnie program wywaliłby czerwony błąd w konsoli i zamknął okienko (Crash). 
   My nauczymy go mówić: "Spróbuj to otworzyć, a JAK wywali błąd, to zrób coś innego, zamiast zdychać".

zmiana w pliku: `main.py`:

Krok 1: Dodaj import na samej górze pliku
-----------------------------------------

```python
import json
```

Krok 2: Nowa funkcja do wyszukiwania haseła
-------------------------------------------
Wklej tę nową funkcję gdzieś nad funkcją save():

```python
# --- WYSZUKIWANIE HASŁA ---
def find_password():
    website = website_entry.get()
    
    # Próbujemy otworzyć plik JSON
    try:
        with open("data.json", "r") as data_file:
            # Wczytanie danych z JSONa do pythonowego słownika
            data = json.load(data_file)
            
    # Jeśli plik jeszcze nie istnieje (FileNotFoundError), rzucamy pop-up
    except FileNotFoundError:
        messagebox.showinfo(title="Error", message="No Data File Found.")
        
    # Jeśli plik się otworzył bez błędu (czyli try przeszło pomyślnie):
    else:
        # Sprawdzamy, czy wpisana strona istnieje w naszym słowniku
        if website in data:
            email = data[website]["email"]
            password = data[website]["password"]
            messagebox.showinfo(title=website, message=f"Email: {email}\nPassword: {password}")
        else:
            messagebox.showinfo(title="Error", message=f"No details for {website} exists.")

```

Krok 3: Przebudowa funkcji save()
---------------------------------

Podmień swoją starą funkcję save() na tę nową, która obsługuje format JSON i błędy. 
Zwróć uwagę, że kłódka (readonly) nadal tu jest!

```python
# --- ZAPISYWANIE HASŁA DO JSON ---
def save():
    website = website_entry.get()
    email = email_entry.get()
    password = password_entry.get()
    
    # Tworzymy strukturę słownika, jakiej wymaga JSON
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
                data = json.load(data_file)
                
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
```


Krok 4: Dodanie przycisku "Search" w interfejsie
------------------------------------------------

Znajdź w swoim kodzie sekcję z website_entry. 
Zmieniamy szerokość pola, żeby zrobić miejsce na nowy przycisk obok niego.
Podmień definicję `website_entry` i dodaj pod nią przycisk szukaj:


# Zmniejszamy szerokość pola z 35 na 17 i zabieramy mu columnspan
website_entry = tk.Entry(width=17)
website_entry.grid(row=1, column=1)
website_entry.focus()

# DODAJEMY PRZYCISK SZUKAJ:
search_button = tk.Button(text="Search", width=14, command=find_password)
search_button.grid(row=1, column=2)

(Pamiętaj, żeby upewnić się, że reszta pól - email_entry, password_entry i inne przyciski - nadal ma poprawne pozycje grid, 
ale z tymi zmianami powyżej powinno wszystko idealnie pasować do siatki).

Dlaczego ta logika jest taka ważna (pod maską):

Początkujący robią tak: otwierają plik, dodają linijkę tekstu, zamykają plik. W JSON to tak nie działa.
JSON to zwarta struktura (jak rosyjska matrioszka). Żeby dopisać nowe hasło do pliku JSON, musisz:
1. Odczytać z pliku WSZYSTKIE dotychczasowe hasła do pamięci RAM (json.load).
2. Dodać do nich to jedno nowe hasło (data.update).
3. Zapisać CAŁOŚĆ z powrotem do pliku, nadpisując stary (json.dump).

A blok `try/except/else/finally` gwarantuje Ci, że jak ktoś na twardo usunie plik data.json z dysku, 
to aplikacja się nie zawiesi, tylko kulturalnie stworzy go na nowo.

Wklej, popraw siatkę i przetestuj:
Dodaj jakieś hasło do Facebooka.
Zobaczysz, że w folderze pojawił się elegancki plik `data.json`.
Skasuj nazwę z pola, wpisz "Facebook" jeszcze raz i kliknij nowy przycisk Search. 
Wyskoczy okienko z zapisanym mailem i hasłem.
Zgodnie z Twoim screenem, dzisiaj (Dzień 24) robimy absolutną podstawę pracy z systemem: 
 - Zapis i odczyt plików tekstowych oraz ścieżki (File I/O).

Teoria w 2 zdaniach (Tylko konkrety):
-------------------------------------

Słowo kluczowe `with` jest używane do: zarządzania zasobami, takimi jak pliki.
Kiedyś pliki otwierało się komendą file = open("plik.txt") i na koniec trzeba było pamiętać o file.close(). 
Teraz pisze się with `open("plik.txt") as file`: i Python sam zamyka plik, gdy skończy z nim pracować. Koniec z wyciekami pamięci.

Tryby: `mode="r"` (read - tylko odczyt), `mode="w"` (write - kasuje wszystko i nadpisuje), `mode="a"` (append - dopisuje na końcu pliku).

Projekt Dnia 24: Mail Merge (Seryjna korespondencja)
----------------------------------------------------

Wyobraź sobie, że pracujesz w biurze i szef każe Ci wysłać 50 takich samych listów do klientów, zmieniając tylko imię na samej górze. 
Zamiast robić to ręcznie (kopiuj-wklej), piszesz skrypt, który robi to w ułamek sekundy.

Utwórz nowy projekt w PyCharmie (np. Day_24_MailMerge).
Stwórz w nim dwa pliki tekstowe (.txt) i jeden plik .py:

Plik 1: invited_names.txt (Lista gości)
---------------------------------------

```text
Aang
Zuko
Appa
Katara
Sokka
```


Plik 2: starting_letter.txt (Szablon listu)
-------------------------------------------

```text
Dear [name],
You are invited to my birthday party this Saturday.
Hope you can make it!
Robert
```


Plik 3: main.py (Twój skrypt)
-----------------------------

```python
PLACEHOLDER = "[name]"

# 1. Otwieramy plik z imionami i czytamy go linijka po linijce
with open("invited_names.txt", mode="r") as names_file:
    # readlines() robi z pliku listę, np.["Aang\n", "Zuko\n"]
    names = names_file.readlines()

# 2. Otwieramy szablon listu i czytamy całą jego treść jako jeden tekst
with open("starting_letter.txt", mode="r") as letter_file:
    letter_contents = letter_file.read()

    # 3. Przechodzimy przez każde imię z listy
    for name in names:
        # strip() usuwa białe znaki (np. niewidzialny enter "\n" na końcu imienia)
        stripped_name = name.strip()
        
        # Podmieniamy słowo "[name]" na konkretne imię
        new_letter = letter_contents.replace(PLACEHOLDER, stripped_name)
        
        # 4. Tworzymy nowy plik dla każdej osoby i zapisujemy w nim gotowy list
        with open(f"letter_for_{stripped_name}.txt", mode="w") as completed_letter:
            completed_letter.write(new_letter)

print("Gotowe. Sprawdź folder z projektem!")
```

Co tu się stało (pod maską):

Użyłeś `readlines()`, żeby wyciągnąć imiona jako listę.

Musiałeś użyć metody .strip(), bo w plikach tekstowych po każdej linijce ukryty jest znak nowej linii (\n). Bez tego list wyglądałby koślawo (enter zaraz po imieniu).

Pętla for przeleciała po każdym imieniu, metoda .replace() podmieniła tekst, a tryb mode="w" automatycznie stworzył 5 nowych plików na Twoim dysku (ponieważ podałeś nazwy plików, które wcześniej nie istniały).

Odpal to. Zobaczysz, jak w ułamku sekundy po lewej stronie w PyCharmie pojawia się 5 gotowych listów (letter_for_Aang.txt, itd.).

To jest automatyzacja nudnej roboty. Od tego momentu umiesz wyciągać dane z plików i zapisywać wyniki na dysku.

Daj znać, czy zadziałało. Jeśli tak, zamykamy Dzień 24 i jutro (albo zaraz) lecimy z Dniem 25 (CSV i Pandas – to już wyższa szkoła jazdy!).
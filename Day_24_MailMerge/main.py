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


import pandas as pd

# 1. Wczytujemy plik CSV do pamięci
data = pd.read_csv("nato_phonetic_alphabet.csv")

# 2. Magia nr 1: Dictionary Comprehension
# Iterujemy po tabeli Pandas wiersz po wierszu i robimy z tego zwykły słownik pythona: {"A": "Alfa", "B": "Bravo"...}
phonetic_dict = {row.letter: row.code for (index, row) in data.iterrows()}

# 3. Pobieramy słowo od użytkownika i od razu zamieniamy na wielkie litery
word = input("Enter a word: ").upper()

# 4. Magia nr 2: List Comprehension
# Przechodzimy po każdej literze wpisanego słowa i wyciągamy jej odpowiednik z naszego słownika
output_list = [phonetic_dict[letter] for letter in word]

# 5. Wypluwamy wynik
print(output_list)
Dzień 26
--------

Dzień 26: NATO Alphabet (Słowniki i List Comprehension)
-------------------------------------------------------

W tym dniu uczysz się, jak zlikwidować wielopoziomowe pętle for i zastąpić je jednym, eleganckim zapisem. 
To odróżnia juniora od mid-developera.

Budujemy program, który pyta o Twoje imię i wypluwa je w alfabecie lotniczym (np. wpisujesz "KUBA", a on wypluwa ['Kilo', 'Uniform', 'Bravo', 'Alfa']).

Potrzebujesz dwóch plików. Żebyś nie musiał szukać plików po kursach, podaję Ci gotowy wsad.

Plik 1: nato_phonetic_alphabet.csv
(Utwórz taki plik tekstowy i wklej to dokładnie tak, jak leci)

```text
letter,code
A,Alfa
B,Bravo
C,Charlie
D,Delta
E,Echo
F,Foxtrot
G,Golf
H,Hotel
I,India
J,Juliet
K,Kilo
L,Lima
M,Mike
N,November
O,Oscar
P,Papa
Q,Quebec
R,Romeo
S,Sierra
T,Tango
U,Uniform
V,Victor
W,Whiskey
X,X-ray
Y,Yankee
Z,Zulu
```


Plik 2: main.py
(Sama esencja, bez zbędnych funkcji)

```python
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
```

Co tu się dzieje pod maską (konkrety):

iterrows(): 
Normalnie w Pythonie ciężko przelatywać pętlą przez tabelę z Pandas. 
`iterrows()` to wbudowany silnik, który tnie tabelę na pojedyncze wiersze, 
dzięki czemu możesz wyciągać dane pisząc po prostu `row.letter` i `row.code`.

Klamerki {} w linijce 9: 
To jest `Dictionary Comprehension`. 
Zamiast tworzyć pusty słownik, pisać pętlę i dodawać klucze, zrobiliśmy to w jednej linii. 
Wzór to: `{nowy_klucz: nowa_wartosc for wiersz in tabela}`.

Nawiasy kwadratowe [] w linijce 15: 
To jest `List Comprehension`. Wzór to: `[zrob_cos_z_elementem for element in słowo]`. 
Przelatuje przez każdą literę Twojego słowa i od razu pakuje wynik do nowej listy.

Zero pieprzenia się z append(), zero pustych list na start. Czysty, profesjonalny kod.

Odpal to, wpisz w konsoli swoje imię bez spacji i zobacz, jak działa. 
To całe mięso z Dnia 26. 
Daj znać, czy weszło, to w Dniu 27 wjedziemy w robienie okienek w Windowsie/Macu (GUI z biblioteką Tkinter).
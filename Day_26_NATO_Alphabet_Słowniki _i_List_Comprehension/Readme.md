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



//////////////////////////////   troche teorii   //////////////////////////////
-------------------------------------------------------------------------------

Zrozumienie Comprehensions (wyrażeń listowych i słownikowych) to moment, w którym przestajesz pisać w Pythonie 
jak w starym C++, a zaczynasz pisać jak prawdziwy Senior Python Developer. 
W branży nazywa się to pisaniem kodu, który jest "Pythonic".

Skoro kod NATO Alphabet już Ci zadziałał, rozbierzmy ten mechanizm na części pierwsze, 
żebyś mógł tego używać we własnych projektach. Bez lania wody – sama mechanika.

List Comprehension (Skracanie list)
-----------------------------------

Wzór, który musisz wryć sobie w pamięć, to:
`[nowy_element for element in stara_lista (opcjonalny if)]`

Przykład z życia: 
Masz listę liczb i chcesz stworzyć nową listę, w której każda liczba jest podniesiona do kwadratu.

Podejście leszcza (4 linijki):

```python
liczby =[1, 2, 3, 4]
kwadraty =[]
for liczba in liczby:
    kwadraty.append(liczba * liczba)
```


Podejście inżyniera (1 linijka):

```python
liczby =[1, 2, 3, 4]
kwadraty = [liczba * liczba for liczba in liczby]
```

 ... i dodanie warunku (IF):
Chcesz tylko kwadraty z liczb parzystych? Dopisujesz if na końcu:

```python
kwadraty_parzyste =[liczba * liczba for liczba in liczby if liczba % 2 == 0]
```

W ułamku sekundy program przejdzie przez listę, odrzuci nieparzyste i wypluje gotowy wynik.


Dictionary Comprehension (Skracanie słowników)
----------------------------------------------

Słowniki (kolekcje typu Klucz: Wartość) działają tak samo, tylko używasz klamerek {} i dwukropka :.

Wzór:
`{nowy_klucz: nowa_wartosc for element in stara_lista}`

W projekcie NATO użyliśmy tego do przerobienia tabeli Pandas na słownik.
Tabela z pliku CSV (Pandas DataFrame) jest ciężka w obsłudze. Słownik jest super szybki.

Ten fragment z Twojego kodu:

```python
phonetic_dict = {row.letter: row.code for (index, row) in data.iterrows()}
```
Działa jak maszyna na taśmie produkcyjnej:
1. data.iterrows() tnie tabelę Pandas na pojedyncze wiersze.
2. Pętla bierze wiersz po wierszu.
3. row.letter (np. "A") staje się kluczem.
4. row.code (np. "Alfa") staje się wartością.
5. Zwraca czysty, błyskawiczny słownik: {"A": "Alfa", "B": "Bravo"}: phonetic_dict.


Finał z NATO Alphabet
---------------------

Kiedy już masz ten słownik, pobierasz słowo od użytkownika, np. "KUBA".
Słowo w Pythonie to pod maską nic innego jak lista liter: ['K', 'U', 'B', 'A'].

Więc robisz List Comprehension:

```python
output_list = [phonetic_dict[letter] for letter in word]
```

Program czyta to od tyłu do przodu (tak najlepiej to rozumieć):

1. Weź każdą literę (letter) ze słowa (word).
2. Wsadź tę literę do naszego słownika: `phonetic_dict[letter]` (np. `phonetic_dict['K']` da Ci "Kilo").
3. To, co słownik wypluje (np. "Kilo"), wrzuć do nowej listy: `output_list`.

Dlaczego to jest takie ważne?
Gdybyś miał bazę 100 000 rekordów, pętla for z append() byłaby zauważalnie wolniejsza i zajmowałaby 
więcej pamięci operacyjnej niż `List Comprehension`. 
Python jest zoptymalizowany pod Comprehensions – wykonuje je na poziomie języka C pod maską, co daje potężnego kopa do wydajności.

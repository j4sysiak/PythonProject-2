Dzień 27
--------

W Dniu 27 w końcu przestajemy pisać w czarnej konsoli. 
Zaczynamy tworzyć prawdziwe aplikacje okienkowe (okienka, przyciski, pola tekstowe), 
które zachowują się jak normalne programy w Windowsie.

Angela robi tu projekt kalkulatora jednostek (Miles to Kilometers Converter).
Tworzysz nowy projekt (np. Day_27_Tkinter) i potrzebujesz tylko jednego pliku main.py.

trochę teorii:
--------------
Zanim wkleisz kod, musisz zrozumieć dwie kluczowe koncepcje, które można streścić w kilku zdaniach:

**kwargs (Nielimitowane argumenty nazwane):
W `Tkinterze` ciągle będziesz widział taki zapis: `tk.Label(text="Kalkulator", font=("Arial", 12), bg="red")`
Dlaczego parametry są wpisywane po nazwie? 
Bo klasa wbudowana w `Tkintera` może przyjąć kilkadziesiąt różnych ustawień (kolory, ramki, czcionki). 
Zamiast zmuszać Cię do wpisywania 50 parametrów w odpowiedniej kolejności, twórcy użyli **kwargs (słownika argumentów).
Wpisujesz tylko to, co chcesz zmienić. 
Reszta ma wartości domyślne.

Siatka `.grid()` zamiast `.pack()`:
Początkujący używają metody `.pack()`, która układa przyciski jeden pod drugim (jak leci). 
To syf, z którym nic nie zrobisz. 
My używamy `.grid(column=x, row=y)`. 
Traktujesz okno programu jak arkusz Excela. Masz pełną kontrolę nad tym, co gdzie leży.


```python
import tkinter as tk

# 1. Tworzymy główne okno programu (zamiast Screen() z żółwia)
window = tk.Tk()
window.title("Mile to Km Converter")
window.minsize(width=300, height=150)
window.config(padx=20, pady=20) # Marginesy wokół okna

# 2. Funkcja, która odpali się po kliknięciu przycisku
def calculate():
    # Pobieramy wpisaną wartość z pola tekstowego (zawsze wraca jako tekst, więc zmieniamy na float)
    miles = float(input_field.get())
    km = round(miles * 1.609, 2)
    # Aktualizujemy tekst w naszym labelu z wynikiem
    result_label.config(text=f"{km}")

# 3. Pole do wpisywania (Entry)
input_field = tk.Entry(width=10)
input_field.grid(column=1, row=0) # Tkinter używa siatki (grid) do układania elementów

# 4. Teksty stałe (Labels)
miles_label = tk.Label(text="Miles", font=("Arial", 12))
miles_label.grid(column=2, row=0)

is_equal_label = tk.Label(text="is equal to", font=("Arial", 12))
is_equal_label.grid(column=0, row=1)

result_label = tk.Label(text="0", font=("Arial", 12, "bold"))
result_label.grid(column=1, row=1)

km_label = tk.Label(text="Km", font=("Arial", 12))
km_label.grid(column=2, row=1)

# 5. Przycisk (Button) - zauważ, że w command=calculate NIE MA nawiasów ()
calculate_button = tk.Button(text="Calculate", command=calculate)
calculate_button.grid(column=1, row=2)

# 6. Pętla główna okna (musi być na samym końcu, inaczej okno się zamknie)
window.mainloop()
```

To jest kompletny kod, który tworzy prosty konwerter mil na kilometry.
Wystarczy go skopiować do pliku main.py i uruchomić.
Zobaczysz okienko, w którym możesz wpisać liczbę mil,kliknąć "Calculate" i od razu zobaczysz wynik w kilometrach.
To jest dopiero początek, ale już widać, jak potężne są możliwości tworzenia interaktywnych aplikacji w Pythonie dzięki bibliotece Tkinter! 

Co tu się wydarzyło (Pod maską):
Biblioteka wbudowana: 
`tkinter` to wbudowana biblioteka Pythona do interfejsów graficznych. 
Nie musisz robić pip install. 

System siatki (.grid()): 
Zamiast podawać współrzędne X i Y jak w żółwiu, w `Tkinterze` układasz elementy jak w tabelce Excela (kolumny i wiersze). 
`column=1, row=0` to środkowa kolumna, najwyższy wiersz.

Event Driven Programming: 
Zwróć uwagę na `command=calculate` w przycisku. 
Przekazujesz tam nazwę funkcji, ale bez nawiasów. 

Mówisz programowi: 
"Pamiętaj o tej funkcji, ale odpal ją dopiero, jak ktoś wciśnie guzik". 
To jest fundament wszystkich aplikacji okienkowych.


Na co zwrócić uwagę (błędy nowicjuszy):
Błąd 1:
-------
Wpisanie `command=calculate()`. 
Jak dasz tam nawiasy, to Python wykona tę funkcję natychmiast przy odpalaniu programu (i wywali błąd, bo pole tekstowe będzie jeszcze puste), 
a nie przy kliknięciu. 
Brak nawiasów oznacza: "Panie Tkinter, trzymaj namiar na tę funkcję w pamięci i odpal ją dopiero jak user kliknie".

Błąd 2:
-------
Zapomnienie o `.grid()`. 
Jeśli stworzysz guzik `tk.Button(...)` ale nie dodasz w kolejnej linijce `.grid()`, on nie pojawi się na ekranie. 
Stworzy się w pamięci RAM, ale system nie będzie wiedział, gdzie go narysować.

Odpal ten kod. Skonwertuj sobie parę mil na kilometry i zobacz, jak płynnie to działa w okienku.



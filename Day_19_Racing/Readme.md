Dobra, wyścigi żółwi. To jest pierwszy moment, kiedy program przestaje być statycznym skryptem, 
a zaczyna być aplikacją sterowaną przez użytkownika.

W tym projekcie tworzymy 6 żółwi, ustawiamy je w rzędzie, a potem każdy z nich w pętli while wykonuje 
losowy krok do przodu, aż któryś przekroczy linię mety.

Projekt: Wyścigi żółwi
----------------------

Tworzysz jeden plik `main.py`. Wklejasz to:

```python
from turtle import Turtle, Screen
import random

# 1. Konfiguracja ekranu
screen = Screen()
screen.setup(width=500, height=400)
user_bet = screen.textinput(title="Make your bet", prompt="Which turtle will win the race? Enter a color: ")

colors = ["red", "orange", "yellow", "green", "blue", "purple"]
y_positions = [-70, -40, -10, 20, 50, 80]
all_turtles = []

# 2. Tworzenie 6 żółwi (instancje klasy Turtle)
for turtle_index in range(0, 6):
    new_turtle = Turtle(shape="turtle")
    new_turtle.color(colors[turtle_index])
    new_turtle.penup()
    new_turtle.goto(x=-230, y=y_positions[turtle_index])
    all_turtles.append(new_turtle)

# 3. Logika wyścigu
is_race_on = False
if user_bet:
    is_race_on = True

while is_race_on:
    for turtle in all_turtles:
        # Sprawdzenie czy żółw dojechał do mety (x = 230)
        if turtle.xcor() > 230:
            is_race_on = False
            winning_color = turtle.pencolor()
            if winning_color == user_bet:
                print(f"You've won! The {winning_color} turtle is the winner!")
            else:
                print(f"You've lost! The {winning_color} turtle is the winner!")
        
        # Każdy żółw robi losowy krok od 0 do 10
        rand_distance = random.randint(0, 10)
        turtle.forward(rand_distance)

screen.exitonclick()
```

Co tu się dzieje (konkrety):

screen.textinput: 
To jest Twoje pierwsze "okno dialogowe". 
Program zatrzymuje się i czeka, aż wpiszesz kolor w okienku.

Lista obiektów (all_turtles): 
Zamiast pisać 6 razy t1 = Turtle(), t2 = Turtle(), robimy to w pętli for. 
To jest potęga programowania – tworzysz armię obiektów jednym ruchem.

Pętla while: 
Wyścig trwa tak długo, aż któryś żółw przekroczy współrzędną x = 230.

turtle.xcor(): 
Każdy obiekt Turtle pamięta swoją pozycję na ekranie. 
Używamy tego, żeby sprawdzić, czy któryś już wygrał.

Odpal to. Wyskoczy okienko, wpisz kolor (np. red albo blue), a potem patrz, jak żółwie zapierdalają do mety.
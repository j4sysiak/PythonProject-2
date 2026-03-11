Zasada jest prosta: żółw idzie do góry, samochody jadą z prawej do lewej, jak walniesz w auto – giniesz.

Oto szkielet, który musisz wkleić.

Plik 1: player.py (Żółw)
------------------------

```python
from turtle import Turtle

STARTING_POSITION = (0, -280)
MOVE_DISTANCE = 10
FINISH_LINE_Y = 280

class Player(Turtle):
    def __init__(self):
        super().__init__()
        self.shape("turtle")
        self.penup()
        self.setheading(90)
        self.go_to_start()

    def go_to_start(self):
        self.goto(STARTING_POSITION)

    def move_up(self):
        self.forward(MOVE_DISTANCE)
```

Plik 2: car_manager.py (Samochody)
----------------------------------

Tu jest najważniejsza logika: generowanie aut i ich przyspieszanie.

```python
from turtle import Turtle
import random

COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]
STARTING_MOVE_DISTANCE = 5
MOVE_INCREMENT = 2

class CarManager:
    def __init__(self):
        self.all_cars = []
        self.car_speed = STARTING_MOVE_DISTANCE

    def create_car(self):
        if random.randint(1, 6) == 1: # Generuje auto średnio co 6 klatek
            new_car = Turtle("square")
            new_car.shapesize(stretch_wid=1, stretch_len=2)
            new_car.penup()
            new_car.color(random.choice(COLORS))
            new_car.goto(300, random.randint(-250, 250))
            self.all_cars.append(new_car)

    def move_cars(self):
        for car in self.all_cars:
            car.backward(self.car_speed)

    def level_up(self):
        self.car_speed += MOVE_INCREMENT
```

Plik 3: main.py (Silnik gry)
----------------------------

Spinamy wszystko.

```python
import time
from turtle import Screen
from player import Player
from car_manager import CarManager
from scoreboard import Scoreboard # Użyj klasy Scoreboard z Ponga/Snake'a

screen = Screen()
screen.setup(width=600, height=600)
screen.tracer(0)

player = Player()
car_manager = CarManager()
scoreboard = Scoreboard() # Musisz mieć klasę Scoreboard

screen.listen()
screen.onkey(player.move_up, "Up")

game_is_on = True
while game_is_on:
    time.sleep(0.1)
    screen.update()
    
    car_manager.create_car()
    car_manager.move_cars()

    # Kolizja z autem
    for car in car_manager.all_cars:
        if car.distance(player) < 20:
            game_is_on = False
            scoreboard.game_over()

    # Przejście na drugą stronę
    if player.ycor() > 280:
        player.go_to_start()
        car_manager.level_up()
        scoreboard.increase_score()

screen.exitonclick()
```

Plik 4: scoreboard.py
---------------------

Oto klasa Scoreboard skrojona pod Turtle Crossing:

```python
from turtle import Turtle

FONT = ("Courier", 24, "normal")

class Scoreboard(Turtle):
    def __init__(self):
        super().__init__()
        self.level = 1
        self.hideturtle()
        self.penup()
        self.goto(-280, 250)
        self.update_scoreboard()

    def update_scoreboard(self):
        self.clear()
        self.write(f"Level: {self.level}", align="left", font=FONT)

    def increase_level(self):
        self.level += 1
        self.update_scoreboard()

    def game_over(self):
        self.goto(0, 0)
        self.write("GAME OVER", align="center", font=FONT)
```

Co tu się zmieniło względem Ponga:
self.level: 
Zamiast dwóch wyników (l_score, r_score), mamy jeden licznik poziomu.

Pozycja: 
self.goto(-280, 250) ustawia napis w lewym górnym rogu ekranu, żeby nie zasłaniał drogi żółwiowi.

increase_level: 
Zamiast dodawać punkt, zwiększamy poziom.



Jak to podpiąć w main.py?
W pętli while, w miejscu gdzie żółw przechodzi na drugą stronę, wywołujesz to tak:

# Przejście na drugą stronę
    if player.ycor() > 280:
        player.go_to_start()
        car_manager.level_up()
        scoreboard.increase_level() # <--- tutaj


Dlaczego to jest "Capstone"?
----------------------------

To projektpodsumowującym, bo musisz tu połączyć:

1. Dziedziczenie (Player dziedziczy po Turtle).
2. Zarządzanie listami (`all_cars` – musisz usuwać auta, które wyjechały poza ekran, żeby nie zapchać pamięci).
3. Logikę gry (zwiększanie prędkości aut `level_up` po każdym udanym przejściu).

Pro-tip: 
W `car_manager.py` w metodzie `move_cars` możesz dodać usuwanie aut, które mają xcor() < -320, żeby nie trzymać tysięcy obiektów w pamięci.

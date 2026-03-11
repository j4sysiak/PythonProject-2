Dzień 21 to rozszerzenie Snake'a o mechanikę gry. 
Teraz wąż musi jeść, rosnąć i kończyć grę przy kolizji ze ścianą lub własnym ogonem.

Wymaga to dodania dwóch nowych klas: `Food` (jedzenie) i `Scoreboard` (wynik).

Plik 1: food.py
---------------

Dziedziczymy po klasie Turtle, żeby nasz obiekt jedzenia miał wszystkie cechy żółwia (pozycja, kształt, kolor).

```python
from turtle import Turtle
import random

class Food(Turtle):
    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.penup()
        self.shapesize(stretch_len=0.5, stretch_wid=0.5)
        self.color("blue")
        self.speed("fastest")
        self.refresh()

    def refresh(self):
        random_x = random.randint(-280, 280)
        random_y = random.randint(-280, 280)
        self.goto(random_x, random_y)
```

Plik 2: scoreboard.py
---------------------

Klasa do wyświetlania tekstu na ekranie.

```python
from turtle import Turtle

class Scoreboard(Turtle):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.color("white")
        self.penup()
        self.goto(0, 270)
        self.hideturtle()
        self.update_scoreboard()

    def update_scoreboard(self):
        self.clear()
        self.write(f"Score: {self.score}", align="center", font=("Arial", 24, "normal"))

    def increase_score(self):
        self.score += 1
        self.update_scoreboard()

    def game_over(self):
        self.goto(0, 0)
        self.write("GAME OVER", align="center", font=("Arial", 24, "normal"))
```

Plik 3: snake.py (Zaktualizowany)
---------------------------------

Musisz dodać metodę extend() do klasy Snake, żeby wąż mógł rosnąć.

```python
# Dodaj to do klasy Snake w pliku snake.py
    def extend(self):
        self.add_segment(self.segments[-1].position())
```

Plik 4: main.py (Zaktualizowany silnik)
---------------------------------------

Tu spinamy wszystko w całość.

```python
from turtle import Screen
from snake import Snake
from food import Food
from scoreboard import Scoreboard
import time

screen = Screen()
screen.setup(width=600, height=600)
screen.bgcolor("black")
screen.tracer(0)

snake = Snake()
food = Food()
scoreboard = Scoreboard()

screen.listen()
screen.onkey(snake.up, "Up")
screen.onkey(snake.down, "Down")
screen.onkey(snake.left, "Left")
screen.onkey(snake.right, "Right")

game_is_on = True
while game_is_on:
    screen.update()
    time.sleep(0.1)
    snake.move()

    # Kolizja z jedzeniem
    if snake.head.distance(food) < 15:
        food.refresh()
        snake.extend()
        scoreboard.increase_score()

    # Kolizja ze ścianą
    if snake.head.xcor() > 290 or snake.head.xcor() < -290 or snake.head.ycor() > 290 or snake.head.ycor() < -290:
        game_is_on = False
        scoreboard.game_over()

    # Kolizja z ogonem
    for segment in snake.segments[1:]:
        if snake.head.distance(segment) < 10:
            game_is_on = False
            scoreboard.game_over()

screen.exitonclick()
```

Co tu się dzieje (konkrety):

Dziedziczenie (super().__init__()): 
Klasy `Food` i `Scoreboard` dziedziczą po `Turtle`. 
Dzięki temu mają dostęp do wszystkich metod żółwia (jak goto, color, write), ale dodajemy im własne funkcjonalności.

distance(): 
To wbudowana metoda klasy Turtle, która oblicza odległość między dwoma obiektami. 
Jeśli jest mniejsza niż 15 pikseli, uznajemy, że wąż zjadł jedzenie.

snake.segments[1:]: 
To tzw. `slicing listy`. 
Sprawdzamy kolizję z każdym segmentem węża oprócz głowy (indeks 0), bo głowa zawsze dotyka samej siebie.

Masz teraz w pełni działającą grę. 
To jest koniec "podstaw" Pythona. 
Dalej zaczynają się biblioteki do GUI (Tkinter), pracy z plikami i API.
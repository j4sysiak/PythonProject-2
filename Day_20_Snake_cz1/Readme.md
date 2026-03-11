Snake to już nie są przelewki. 
To pierwszy projekt, w którym musisz zarządzać stanem wielu obiektów. 
Wąż to lista żółwi (segmentów), które muszą się poruszać jeden za drugim.

Żeby to było czytelne i profesjonalne, dzielimy to na 3 klasy (pliki).

Plik 1: snake.py (Logika węża)
------------------------------

To jest "mózg" węża. Odpowiada za tworzenie ciała, ruch i skręcanie.

```python
from turtle import Turtle

STARTING_POSITIONS = [(0, 0), (-20, 0), (-40, 0)]
MOVE_DISTANCE = 20
UP = 90
DOWN = 270
LEFT = 180
RIGHT = 0

class Snake:
    def __init__(self):
        self.segments = []
        self.create_snake()
        self.head = self.segments[0]

    def create_snake(self):
        for position in STARTING_POSITIONS:
            self.add_segment(position)

    def add_segment(self, position):
        new_segment = Turtle("square")
        new_segment.color("white")
        new_segment.penup()
        new_segment.goto(position)
        self.segments.append(new_segment)

    def move(self):
        # Każdy segment musi wskoczyć na miejsce poprzedniego (od tyłu)
        for seg_num in range(len(self.segments) - 1, 0, -1):
            new_x = self.segments[seg_num - 1].xcor()
            new_y = self.segments[seg_num - 1].ycor()
            self.segments[seg_num].goto(new_x, new_y)
        self.head.forward(MOVE_DISTANCE)

    def up(self):
        if self.head.heading() != DOWN:
            self.head.setheading(UP)

    def down(self):
        if self.head.heading() != UP:
            self.head.setheading(DOWN)

    def left(self):
        if self.head.heading() != RIGHT:
            self.head.setheading(LEFT)

    def right(self):
        if self.head.heading() != LEFT:
            self.head.setheading(RIGHT)
```

Plik 2: main.py (Silnik gry)
----------------------------

Tutaj łączymy wszystko: ekran, węża i sterowanie.

```python
from turtle import Screen
from snake import Snake
import time

screen = Screen()
screen.setup(width=600, height=600)
screen.bgcolor("black")
screen.title("Snake Game")
screen.tracer(0) # Wyłącza animację, żeby wąż nie "skakał"

snake = Snake()

screen.listen()
screen.onkey(snake.up, "Up")
screen.onkey(snake.down, "Down")
screen.onkey(snake.left, "Left")
screen.onkey(snake.right, "Right")

game_is_on = True
while game_is_on:
    screen.update() # Ręczne odświeżanie ekranu
    time.sleep(0.1) # Spowolnienie pętli
    snake.move()

screen.exitonclick()
```

Co tu się dzieje (konkrety):

screen.tracer(0) i screen.update(): 
To jest kluczowe. 
Domyślnie turtle rysuje każdy ruch żółwia. 
Przy wężu wyglądałoby to jak miganie. 
Wyłączamy to (tracer(0)), wykonujemy wszystkie obliczenia w pamięci, a potem jednym strzałem (update()) rysujemy gotową klatkę.

Logika ruchu: 
Zauważ pętlę w snake.move(). 
Zaczynamy od ostatniego segmentu i przesuwamy go na pozycję przedostatniego. 
Dzięki temu wąż "podąża" za głową.

screen.listen(): 
To jest nasłuchiwacz klawiatury. 
Bez tego program nie reagowałby na strzałki.



Jak to zadziała, to masz już szkielet gry. 
W Dniu_21 Angela dodaje jedzenie (Food) i tablicę wyników (Scoreboard). 




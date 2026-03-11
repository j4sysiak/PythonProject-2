Dzień 22 to Pong. 
Klasyka gier wideo.

W tym dniu Angela uczy, jak stworzyć grę, w której masz dwa paletki i piłkę, która odbija się od ścian i paletek. 
Z punktu widzenia programowania, to jest test Twojej umiejętności zarządzania kolizjami (`Collision Detection`).

Co nowego w Dniu 22:
--------------------
Wykrywanie kolizji z obiektami: Musisz sprawdzić, czy współrzędne piłki pokrywają się z współrzędnymi paletki - `Collision Detection`.
Dynamiczna prędkość: Piłka musi przyspieszać po każdym odbiciu od paletki.
Sterowanie dwoma graczami: Jeden gracz używa strzałek, drugi klawiszy W i S.

Plik 1: paddle.py (Klasa paletki)
---------------------------------

Dziedziczy po Turtle, żeby mieć gotowe metody ruchu.

```python
from turtle import Turtle

class Paddle(Turtle):
    def __init__(self, position):
        super().__init__()
        self.shape("square")
        self.color("white")
        self.shapesize(stretch_wid=5, stretch_len=1)
        self.penup()
        self.goto(position)

    def go_up(self):
        new_y = self.ycor() + 20
        self.goto(self.xcor(), new_y)

    def go_down(self):
        new_y = self.ycor() - 20
        self.goto(self.xcor(), new_y)
```

Plik 2: ball.py (Klasa piłki)
-----------------------------

Piłka musi wiedzieć, jak się poruszać i jak odbijać.

```python
from turtle import Turtle

class Ball(Turtle):
    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.color("white")
        self.penup()
        self.x_move = 10
        self.y_move = 10
        self.move_speed = 0.1

    def move(self):
        new_x = self.xcor() + self.x_move
        new_y = self.ycor() + self.y_move
        self.goto(new_x, new_y)

    def bounce_y(self):
        self.y_move *= -1 # Odwrócenie kierunku pionowego

    def bounce_x(self):
        self.x_move *= -1 # Odwrócenie kierunku poziomego
        self.move_speed *= 0.9 # Przyspieszenie piłki

    def reset_position(self):
        self.goto(0, 0)
        self.move_speed = 0.1
        self.bounce_x()
```

Plik 3: main.py (Silnik gry)
----------------------------

Tu łączymy wszystko.

```python
from turtle import Screen
from paddle import Paddle
from ball import Ball
from scoreboard import Scoreboard
import time

screen = Screen()
screen.bgcolor("black")
screen.setup(width=800, height=600)
screen.tracer(0)

r_paddle = Paddle((350, 0))
l_paddle = Paddle((-350, 0))
ball = Ball()
scoreboard = Scoreboard()

screen.listen()
screen.onkey(r_paddle.go_up, "Up")
screen.onkey(r_paddle.go_down, "Down")
screen.onkey(l_paddle.go_up, "w")
screen.onkey(l_paddle.go_down, "s")

game_is_on = True
while game_is_on:
    time.sleep(ball.move_speed)
    screen.update()
    ball.move()

    # Kolizja ze ścianą (góra/dół)
    if ball.ycor() > 280 or ball.ycor() < -280:
        ball.bounce_y()

    # Kolizja z paletkami
    if ball.distance(r_paddle) < 50 and ball.xcor() > 320 or ball.distance(l_paddle) < 50 and ball.xcor() < -320:
        ball.bounce_x()

    # Piłka poza ekranem (punkt dla gracza)
    if ball.xcor() > 380:
        ball.reset_position()
        scoreboard.l_point()
    if ball.xcor() < -380:
        ball.reset_position()
        scoreboard.r_point()

screen.exitonclick()
```

Oto klasa Scoreboard przygotowana specjalnie pod Ponga (Dzień 22). 
Musi ona obsługiwać dwa wyniki (lewy i prawy gracz), więc jest nieco bardziej rozbudowana niż ta z węża.

Wklej to do pliku scoreboard.py:
--------------------------------

```python
from turtle import Turtle

class Scoreboard(Turtle):
    def __init__(self):
        super().__init__()
        self.color("white")
        self.penup()
        self.hideturtle()
        self.l_score = 0
        self.r_score = 0
        self.update_scoreboard()

    def update_scoreboard(self):
        self.clear()
        # Wynik lewego gracza
        self.goto(-100, 200)
        self.write(self.l_score, align="center", font=("Courier", 80, "normal"))
        # Wynik prawego gracza
        self.goto(100, 200)
        self.write(self.r_score, align="center", font=("Courier", 80, "normal"))

    def l_point(self):
        self.l_score += 1
        self.update_scoreboard()

    def r_point(self):
        self.r_score += 1
        self.update_scoreboard()
```

Co tu się dzieje (konkrety):

self.clear(): 
To najważniejsza metoda w tej klasie. 
Zanim wypiszemy nowy wynik, musimy wyczyścić stary z ekranu, inaczej liczby będą się na siebie nakładać i zrobi się nieczytelny syf.

Dwie zmienne: 
self.l_score i self.r_score trzymają stan punktów dla obu graczy.

self.write(): 
To metoda klasy Turtle, która "pisze" tekst na ekranie graficznym. 
Ustawiamy czcionkę "Courier" (wygląda jak w starych grach), rozmiar 80 i wyśrodkowanie.

Jak to podpiąć w main.py?
W pętli `while w main.py`, którą Ci wcześniej wysłałem, masz te linijki:

```python
# Piłka poza ekranem (punkt dla gracza)
    if ball.xcor() > 380:
        ball.reset_position()
        scoreboard.l_point() # <--- tutaj wywołujesz metodę z tej klasy
    if ball.xcor() < -380:
        ball.reset_position()
        scoreboard.r_point() # <--- tutaj wywołujesz metodę z tej klasy
```


Co tu jest najważniejsze (konkrety):

self.x_move i self.y_move: To wektory prędkości. Zamiast pisać forward(), zmieniamy współrzędne x i y w każdej klatce. To daje nam pełną kontrolę nad kątem odbicia.

bounce_x i bounce_y: Mnożenie przez -1 to najprostszy sposób na "odbicie" od ściany.

ball.distance(paddle) < 50: To jest klucz do wykrywania kolizji. Jeśli piłka jest wystarczająco blisko paletki, zmieniamy jej kierunek.

To jest ostatni projekt z "Turtle". Od Dnia 23 wchodzimy w prace z plikami CSV i biblioteką Pandas (analiza danych). To już nie jest zabawa, tylko narzędzia, których używa się w prawdziwej pracy.




To wszystko. 
Pong gotowy. 
Jak to odpalisz i działa, to kończymy z żółwiami i wchodzimy w Dzień 23, czyli wczytywanie danych z plików CSV. 
To już jest czysta inżynieria danych, bez żadnych "gier". Gotowy?


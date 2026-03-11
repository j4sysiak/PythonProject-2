from turtle import Turtle
import random

class Food(Turtle):

    # Dziedziczenie (super().__init__()):
    # Klasy Food i Scoreboard dziedziczą po Turtle.
    # Dzięki temu mają dostęp do wszystkich metod żółwia (jak goto, color, write), ale dodajemy im też własne funkcjonalności.
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
        self.goto(random_x, random_y)  # teleportuje obiekt Turtle (obiekt Food) do tego punktu.
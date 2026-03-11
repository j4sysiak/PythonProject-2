from turtle import Turtle

class Scoreboard(Turtle):

    # Dziedziczenie (super().__init__()):
    # Klasy Food i Scoreboard dziedziczą po Turtle.
    # Dzięki temu mają dostęp do wszystkich metod żółwia (jak goto, color, write), ale dodajemy im też własne funkcjonalności.
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
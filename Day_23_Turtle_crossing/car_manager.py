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
        for car in self.all_cars[:]:  # Iterujemy po kopii listy, aby móc usuwać elementy z oryginalnej listy
            car.backward(self.car_speed)
            if car.xcor() < -320:
                car.hideturtle()
                self.all_cars.remove(car)


    def level_up(self):
        self.car_speed += MOVE_INCREMENT
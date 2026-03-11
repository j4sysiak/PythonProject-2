import turtle as t
import random

# 1. Konfiguracja żółwia i ekranu
t.colormode(255) # Pozwala używać kolorów RGB (0-255)
tim = t.Turtle()
tim.speed("fastest") # Maksymalna prędkość rysowania
tim.penup() # Podnosimy pisak, żeby żółw nie zostawiał ciągłej linii
tim.hideturtle() # Ukrywamy samą ikonkę żółwia, interesują nas tylko kropki

# 2. Paleta kolorów RGB (Krotki / Tuples)
color_list =[
    (202, 164, 109), (150, 75, 49), (223, 201, 135), (52, 93, 124),
    (172, 154, 40), (140, 30, 19), (133, 163, 185), (198, 91, 71),
    (46, 122, 86), (72, 43, 35), (145, 178, 148), (13, 99, 71),
    (233, 175, 164), (161, 142, 158), (105, 74, 77), (55, 46, 50),
    (183, 205, 171), (36, 60, 74), (18, 86, 90), (81, 148, 129),
    (148, 17, 20), (14, 70, 64), (30, 68, 100), (107, 127, 153)
]

# 3. Ustawienie pozycji startowej (przesuwamy żółwia w lewy dolny róg ekranu)
tim.setheading(225)
tim.forward(300)
tim.setheading(0)

# 4. Główna pętla rysująca (10x10 kropek)
number_of_dots = 100

for dot_count in range(1, number_of_dots + 1):
    # Rysuj kropkę o wielkości 20, wybierz losowy kolor z listy
    tim.dot(20, random.choice(color_list))
    tim.forward(50) # Przesuń się o 50 pikseli w prawo

    # Jeśli narysowaliśmy 10 kropek w rzędzie, wracamy na początek wyższego rzędu
    if dot_count % 10 == 0:
        tim.setheading(90) # Obrót w górę
        tim.forward(50)    # Krok w górę
        tim.setheading(180)# Obrót w lewo
        tim.forward(500)   # Powrót na początek linii (10 * 50 pikseli)
        tim.setheading(0)  # Obrót w prawo (gotowy do nowej linii)

# 5. Zatrzymanie ekranu (żeby okno nie zamknęło się od razu po narysowaniu)
screen = t.Screen()
screen.exitonclick()
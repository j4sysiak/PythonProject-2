Koniec z czarnym ekranem terminala. W Dniu 18 wjeżdża grafika. Używamy wbudowanego w Pythona modułu Turtle (Żółw), żeby rysować po ekranie.

Angela w tym dniu przez 2 godziny każe rysować kwadraty, trójkąty i inne pierdoły, żeby na koniec zrobić projekt: Obraz z kropek w stylu Damiena Hirsta (taki nowoczesny obraz, który sprzedał się za miliony dolarów).

My omijamy te przedszkolne szlaczki i od razu piszemy finalny projekt.

Teoria w 3 zdaniach (Tylko to, co nowe):

Moduł wbudowany: turtle to biblioteka, którą Python ma w sobie od nowości. Nie musisz używać pip install. Po prostu piszesz import turtle.

Aliasy: Żeby nie pisać w kółko słowa turtle, importujemy go ze skrótem: import turtle as t. Od teraz t to nasz żółw.

Krotki (Tuples): To nowa struktura danych. Wygląda jak lista, ale używa nawiasów okrągłych: (255, 0, 0). Różnica? Krotki są niezmienne. Jak raz ją stworzysz, nie możesz podmienić w niej wartości. Używa się ich np. do definiowania kolorów RGB.

Projekt Dnia 18: Hirst Painting (Obraz z kropek)

Tworzysz w PyCharmie nowy projekt (np. Day_18_Turtle).
Tym razem potrzebujesz tylko jednego pliku – main.py.

Wklej do niego poniższy kod. Zawarłem w nim od razu gotową paletę kolorów RGB (żebyś nie musiał instalować dodatkowych paczek do wyciągania kolorów ze zdjęć, co Angela robi w połowie lekcji i co tylko niepotrzebnie komplikuje sprawę).

Plik: main.py

code
Python
download
content_copy
expand_less
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
Co tu się dzieje (po męsku):

Tworzymy obiekt tim z klasy Turtle.

Mówimy mu: "podnieś pisak (penup), żebyś nie mazał po ekranie, tylko stawiaj kropki (dot)".

Pętla for kręci się 100 razy. Żółw stawia kropkę w losowym kolorze, idzie w prawo.

Instrukcja if dot_count % 10 == 0 to prosty trik matematyczny (modulo). Oznacza: "jeśli numer kropki dzieli się przez 10 bez reszty (czyli jesteśmy na końcu rzędu), to zrób nawrót jak karetka maszyny do pisania – idź w górę i cofnij się na lewą stronę".

Odpal to w PyCharmie. Wyskoczy nowe, białe okienko i w ułamku sekundy wygeneruje Ci obraz. Jak klikniesz w to okienko, to się zamknie.

Dzień 18 z głowy. Daj znać jak zadziała, to w Dniu 19 zrobimy z tego żółwia prawdziwą grę – wyścigi, gdzie będziesz sterował z klawiatury.



/////////////////////


Dokładnie tak. Kurwa, to tylko kropki.

Angela w kursie podnieca się tym projektem, bo to odtworzenie "sztuki nowoczesnej" Damiena Hirsta – gościa, który dosłownie namalował kropki na płótnie i sprzedał to za grube miliony dolarów. Wizualnie to jest nuda i absurd.

Ale z punktu widzenia programisty, te kropki to był tylko pretekst. Ten nudny skrypt miał Ci wbić do głowy trzy konkretne rzeczy pod maską:

Operator Modulo (%): Zobacz na linijkę if dot_count % 10 == 0. To jest zajebiście ważny mechanizm. Używa się go, żeby powiedzieć programowi: "Rób coś w kółko, ale co 10 kroków zrób przerwę/zmień linię/wyślij raport". To klasyczny "powrót karetki".

Krotki (Tuples): Te nawiasy okrągłe z kolorami np. (202, 164, 109). Nauczyłeś się, że w Pythonie są listy, których nie da się zmienić po utworzeniu. Idealne do trzymania stałych danych, jak kolory RGB czy współrzędne GPS.

Pętle i obiekty: Zmusiłeś obiekt (żółwia), żeby sam odwalił powtarzalną, fizyczną robotę 100 razy, podczas gdy Ty napisałeś tylko kilkanaście linijek kodu.

Skoro kropki Cię wkurwiają (i słusznie, bo ile można patrzeć na statyczny obrazek), to zamykamy ten projekt w cholerę.

Wjeżdżamy w Dzień 19: Interakcja i Wyścigi

Koniec z biernym patrzeniem. W Dniu 19 uczysz się dwóch najważniejszych rzeczy w aplikacjach okienkowych:

Event Listeners (Nasłuchiwanie zdarzeń): Program czeka, aż wciśniesz konkretny klawisz na klawiaturze i dopiero wtedy reaguje.

Wiele instancji (Obiektów): Stworzysz 6 niezależnych żółwi z jednej klasy, ustawisz je na linii startu i zrobisz z nich wyścig oparty na losowości.

Twórz nowy projekt w PyCharmie (np. Day_19_Racing).
Daj znać, czy jesteś gotowy, to wrzucam Ci od razu czysty kod na wyścigi – bez lania wody, odpalasz i patrzysz, jak obiekty w końcu robią coś dynamicznego. Lecimy?




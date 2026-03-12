import turtle
import pandas as pd

# 1. Konfiguracja ekranu i wgranie obrazka (Turtle obsługuje tylko format .gif)
screen = turtle.Screen()
screen.title("U.S. States Game")
image = "blank_states_img.gif"
screen.addshape(image)
turtle.shape(image)

# 2. Wczytanie danych z CSV za pomocą Pandas (jedna linijka!)
data = pd.read_csv("50_states.csv")
all_states = data.state.to_list()  # Wyciągamy kolumnę 'state' i robimy z niej zwykłą listę
guessed_states = []

# 3. Główna pętla gry
while len(guessed_states) < 50:
    # Okienko do wpisywania (.title() od razu robi z "texas" -> "Texas")
    answer_state = screen.textinput(title=f"{len(guessed_states)}/50 States Correct",
                                    prompt="What's another state's name?").title()

    # Ukryta komenda do wyjścia z gry i wygenerowania raportu
    if answer_state == "Exit":
        # Szybkie wyciągnięcie brakujących stanów (tzw. List Comprehension)
        missing_states = [state for state in all_states if state not in guessed_states]

        # Tworzymy nową tabelę (DataFrame) z brakujących stanów i zapisujemy do CSV
        new_data = pd.DataFrame(missing_states)
        new_data.to_csv("states_to_learn.csv")
        break

    # Jeśli wpisany stan jest na liście wszystkich stanów:
    if answer_state in all_states:
        guessed_states.append(answer_state)

        # Tworzymy "jednorazowego" żółwia, żeby wypisał tekst na mapie
        t = turtle.Turtle()
        # t.hideturtle()
        # t.penup()

        # Filtrowanie w Pandas: Wyciągamy tylko ten jeden wiersz, gdzie stan to nasza odpowiedź
        state_data = data[data.state == answer_state]

        print(state_data)  # To jest tylko po to, żeby zobaczyć, jak wygląda ten wiersz (jest to DataFrame z jednym wierszem)


        # Przesuwamy żółwia na współrzędne z tego wiersza (.item() wyciąga czystą liczbę)
        t.goto(int(state_data.x.item()), int(state_data.y.item()))
        t.write(answer_state)
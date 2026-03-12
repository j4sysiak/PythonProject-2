Wchodzimy w Dzień 25. 
To jest przełom. 
Kończymy zabawę w wbudowane moduły i instalujemy Pandas – najpotężniejszą bibliotekę do analizy danych w Pythonie. 
To jest "Excel na sterydach", narzędzie używane przez każdego Data Scientista na świecie.

Angela w tym dniu pokazuje, jak bolesne jest czytanie plików CSV za pomocą wbudowanych narzędzi, a potem wjeżdża z Pandasem,
który robi to w jednej linijce.

Krok 1: Instalacja Pandas
-------------------------

Zanim napiszesz linijkę kodu, musisz to pobrać. Wiesz już jak to działa:

Otwierasz Terminal w PyCharmie (upewnij się, że masz (.venv) na początku).

Wpisujesz: `pip install pandas`

Czekasz na zielony komunikat sukcesu.

Teoria w 3 zdaniach (Tylko konkrety):
-------------------------------------

DataFrame: 
To po prostu tabela (arkusz kalkulacyjny) w pamięci programu (ma wiersze i kolumny).

Series: 
To pojedyncza kolumna z tej tabeli (wyciągnięta lista danych).

Wyciąganie danych w Pandas to czysta magia. 
Zamiast pisać pętle for, piszesz np. data[data.temperatura == "max"] i masz wynik w ułamku sekundy.

Projekt Dnia:   Day_25_Zgadywanka_stanów_USA
--------------------------------------------

Tu mała uwaga – żeby ten kod zadziałał, musisz pobrać dwa pliki z materiałów kursu na Udemy do Dnia 25:

1. blank_states_img.gif (pusta mapa USA).
2. 50_states.csv (tabela z nazwami stanów i ich współrzędnymi X, Y na tej mapie).

Wrzuć oba te pliki luzem do głównego folderu swojego nowego projektu w PyCharmie (obok pliku main.py).

Plik: main.py

```python
import pandas as pd

# 1. Konfiguracja ekranu i wgranie obrazka (Turtle obsługuje tylko format .gif)
screen = turtle.Screen()
screen.title("U.S. States Game")
image = "blank_states_img.gif"
screen.addshape(image)
turtle.shape(image)

# 2. Wczytanie danych z CSV za pomocą Pandas (jedna linijka!)
data = pd.read_csv("50_states.csv")
all_states = data.state.to_list() # Wyciągamy kolumnę 'state' i robimy z niej zwykłą listę
guessed_states =[]

# 3. Główna pętla gry
while len(guessed_states) < 50:
    # Okienko do wpisywania (.title() od razu robi z "texas" -> "Texas")
    answer_state = screen.textinput(title=f"{len(guessed_states)}/50 States Correct",
                                    prompt="What's another state's name?").title()

    # Ukryta komenda do wyjścia z gry i wygenerowania raportu
    if answer_state == "Exit":
        # Szybkie wyciągnięcie brakujących stanów (tzw. List Comprehension)
        missing_states =[state for state in all_states if state not in guessed_states]
        
        # Tworzymy nową tabelę (DataFrame) z brakujących stanów i zapisujemy do CSV
        new_data = pd.DataFrame(missing_states)
        new_data.to_csv("states_to_learn.csv")
        break

    # Jeśli wpisany stan jest na liście wszystkich stanów:
    if answer_state in all_states:
        guessed_states.append(answer_state)
        
        # Tworzymy "jednorazowego" żółwia, żeby wypisał tekst na mapie
        t = turtle.Turtle()
        t.hideturtle()
        t.penup()
        
        # Filtrowanie w Pandas: Wyciągamy tylko ten jeden wiersz, gdzie stan to nasza odpowiedź
        state_data = data[data.state == answer_state]
        
        # Przesuwamy żółwia na współrzędne z tego wiersza (.item() wyciąga czystą liczbę)
        t.goto(int(state_data.x.item()), int(state_data.y.item()))
        t.write(answer_state)
```

Co tu jest najważniejsze (pod maską):

Filtrowanie (SQL-style): 
Spójrz na `data[data.state == answer_state]`. 
W klasycznym Pythonie musiałbyś otworzyć plik, napisać pętlę przelatującą przez 50 linijek, dodać if'a i wyciągnąć wynik.
W Pandas robisz to tak, jakbyś gadał z bazą danych. "Daj mi ten wiersz, gdzie kolumna state równa się Texas".

Eksport do CSV:
Linijki `new_data = pd.DataFrame(...)` oraz `.to_csv(...)`. 
Zwykłą listę pythonową zamieniłeś w tabelę i w ułamku sekundy wyplułeś na dysk gotowy raport-plik: `states_to_learn.csv`. 
W prawdziwej pracy to jest złoto.

List Comprehension: 
Zobacz to: `[state for state in all_states if state not in guessed_states]`. To jest bardzo "pythonowy" sposób na skracanie 
pętli for z if'em wewnątrz do jednej, krótkiej linijki. 
Będziesz tego używał non stop.

Zadanie dla Ciebie:
Pobierz te dwa pliki z Udemy, zainstaluj pandas, wklej kod i odpal. 
Jak wpiszesz "Exit", program wyłączy się i sam wygeneruje plik CSV z raportem stanów, których nie zgadłeś.

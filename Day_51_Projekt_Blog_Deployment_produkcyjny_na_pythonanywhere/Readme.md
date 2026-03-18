Dzień 51
--------

Day_51_Projekt_Blog_Deployment_produkcyjny_na_pythonanywhere
------------------------------------------------------------


Wjeżdżamy na produkcję. 
To jest najważniejszy moment w życiu każdego programisty. 
Wychodzimy z piaskownicy 127.0.0.1 do prawdziwego internetu. 
Kiedy to skończymy, wyślesz linka z telefonu do kumpla albo szefa i oni zobaczą Twoją aplikację.

Użyjemy PythonAnywhere – to darmowy, linuxowy serwer w chmurze, idealny do hostowania aplikacji Flask.

Oto instrukcja wdrożenia (Deploymentu) "krok po kroku, bez lania wody". 
Skup się, bo serwery Linuxowe nie wybaczają literówek.

Krok 1: Przygotuj paczkę (U siebie na Windowsie)
------------------------------------------------

Nie rzucamy na serwer śmieci.
Wejdź do folderu ze swoim projektem na dysku.
Zaznacz plik:
1. main.py
2. folder templates
3. folder instance (z Twoją bazą danych).

Nie zaznaczaj folderu .venv ani .idea! (Serwer Linuxowy ma własnego Pythona, pliki z Windowsa go tylko zepsują).

Spakuj te 3 rzeczy do zwykłego archiwum `projekt.zip`.

Krok 2: Załóż konto i wrzuć pliki
---------------------------------

Wejdź na pythonanywhere.com i załóż darmowe konto (Create a Beginner account). 
Twój login będzie częścią Twojej domeny (np. login.pythonanywhere.com).
j4sysiak / W...4

Po zalogowaniu, w głównym panelu (Dashboard) kliknij w zakładkę Files (Pliki) na górze.

Jesteś w swoim katalogu domowym (/home/j4sysiak).

Kliknij żółty przycisk Upload a file i wgraj swój plik projekt.zip.

Krok 3: Rozpakuj pliki (Terminal Linuxa)
----------------------------------------

Kliknij zakładkę Consoles (Konsole) na górze strony.

W sekcji "Start a new console" wybierz Bash (to taki linuksowy odpowiednik CMD).

Otworzy się czarny terminal. Wpisz komendę, żeby rozpakować pliki (zatwierdź Enterem):
`unzip projekt.zip -d moj_blog`
(Zostanie utworzony folder moj_blog, w którym wylądują Twoje pliki).

Teraz zainstalujemy paczki, których wymaga Twój kod. Wpisz w konsoli:
`pip3.10 install --user flask flask-sqlalchemy flask-login werkzeug requests`
(Poczekaj, aż Linux ściągnie i zainstaluje biblioteki).

Krok 4: Skonfiguruj Aplikację Webową
------------------------------------

Kliknij na samej górze w zakładkę Web.
Kliknij duży przycisk Add a new web app.
Kliknij Next.

BARDZO WAŻNE: 
Z listy frameworków wybierz `Manual configuration (including virtualenvs)`. 
Nie wybieraj "Flask", bo ich kreator narobi bałaganu w strukturze plików.

Wybierz wersję Pythona (najlepiej `Python 3.10`). 
Kliknij Next.

Krok 5: Połącz serwer ze swoim kodem (Plik WSGI)
------------------------------------------------

Teraz musimy powiedzieć serwerowi Apache/Nginx, gdzie leży Twój plik `main.py`. 
To miejsce, gdzie wykłada się 90% początkujących.

Będąc w zakładce Web, zjedź w dół do sekcji Code.

Znajdziesz tam link do pliku konfiguracyjnego (będzie się nazywał jakoś tak: `/var/www/j4sysiak_pythonanywhere_com_wsgi.py`). 
Kliknij w niego.

Otworzy się edytor kodu.
Usuń wszystko co tam jest i wklej ten krótki, inżynierski kod:

```python
import sys
import os

# 1. Wskazujemy folder z Twoim rozpakowanym kodem
# ZAMIEŃ 'twoj_login' NA SWÓJ PRAWDZIWY LOGIN Z PYTHONANYWHERE!
path = '/home/j4sysiak/moj_blog'

if path not in sys.path:
    sys.path.append(path)

# 2. To jest poprawka dla bazy danych SQLite, żeby wiedziała gdzie ma pracować
os.chdir(path)

# 3. Importujemy aplikację Flask z pliku main.py
# W PythonAnywhere musi się ona nazywać "application", więc robimy alias (as)
from main import app as application
```


Zapisz plik (zielony przycisk Save na górze) i wróć do zakładki Web.

Krok Ostateczny: Odpal silnik!
-----------------------------

W zakładce Web, na samej górze znajdziesz wielki, zielony przycisk Reload `j4sysiak.pythonanywhere.com`. 
Kliknij go (musisz to robić zawsze, gdy zmienisz coś w kodzie).

Powyżej przycisku znajduje się link do Twojej strony (np. http://j4sysiak.pythonanywhere.com). 
Kliknij go!

BUM!
Jeśli zrobiłeś wszystko krok po kroku, zobaczysz swoją aplikację na żywo w internecie. 
Możesz wejść na http://j4sysiak.pythonanywhere.com/api/posts i zobaczyć swojego JSONa. 
Możesz się zalogować. 
Baza danych działa, wpisy się zapisują.

Przejdź przez to i daj znać. Jak zobaczysz swoją apkę pod publicznym adresem URL, 
to znaczy, że oficjalnie przeszedłeś całą drogę od napisania linijki kodu do wdrożenia na produkcję. \

Wszystko dziala.
---------------


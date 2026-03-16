Dzień 36
--------

Day_36_Selenium_Robot_Klika__Automatyzacja_strony_z_zadaniami
-------------------------------------------------------------

Wchodzimy w ciężką artylerię. 
Selenium to nie jest już "pobieranie danych" – to jest robot-przeglądarka. 
Tam, gdzie `BeautifulSoup` wymięka, bo strona wymaga zalogowania, kliknięcia w menu albo dynamicznego ładowania przez JavaScript, 
`Selenium` wchodzi jak nóż w masło.

Krok 1: Instalacja (po męsku)
-----------------------------

W terminalu (wewnątrz .venv):
`pip install selenium`

Krok 2: WebDriver
-----------------

Selenium potrzebuje "sterownika", żeby gadać z przeglądarką.

Ważne: Dzisiaj Selenium (wersja 4+) samo pobiera sterownik (webdriver-manager), 
więc nie musisz już ręcznie ściągać plików .exe i wrzucać ich do folderów systemowych. 
To ogromny przeskok w porównaniu do tego, co Angela może pokazywać w swoich starych filmach.

Zadanie:
--------
Zrobimy skrypt, który wejdzie na tę stronę z zadaniami dla botów i będzie "klikał" w ciasteczko (Cookie Clicker). 
To idealny test: sprawdza czy umiesz znaleźć element na stronie i wykonać na nim akcję `.click()`.

Wklej to do main.py:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# 1. Inicjalizacja przeglądarki (Chrome)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True) # Żeby okno nie zamykało się od razu
driver = webdriver.Chrome(options=chrome_options)

# 2. Otwieramy stronę
driver.get("http://orteil.dashnet.org/experiments/cookie/")

# 3. Znajdź ciasteczko (element z ID "cookie")
cookie = driver.find_element(By.ID, value="cookie")

# 4. Pętla klikania przez 5 sekund
timeout = time.time() + 5
while time.sleep(0.01) is None: # Trik na nieskończoną pętlę
    cookie.click()
    
    # Warunek wyjścia z pętli po 5 sekundach
    if time.time() > timeout:
        break

# driver.quit() # Odkomentuj to, jeśli chcesz, żeby robot zamykał okno po zakończeniu
```

Co tu jest najważniejsze (Inżynieria):
--------------------------------------

By.ID / By.CSS_SELECTOR / By.XPATH: 
To są sposoby lokalizacji elementów.

ID – najszybsze, jeśli strona ma unikalne ID.

XPATH – absolutny "wymiatacz". 
Pozwala znaleźć element nawet jeśli nie ma ID, np. "znajdź trzeci przycisk w trzecim divie".

driver.click(): 
To jest fizyczna symulacja kliknięcia. 
Przeglądarka myśli, że to człowiek klika.

driver.quit(): 
Nigdy nie zostawiaj otwartych procesów przeglądarki w pamięci RAM, 
bo przy 100 skryptach komputer Ci klęknie. 
Zawsze zamykaj.

Dlaczego to jest "zajebiste" dla Twojego szefa?
Wyobraź sobie, że musisz wejść na portal, wpisać login, hasło, przejść przez 3 podstrony, kliknąć "Generuj raport" i zapisać plik.

Zwykły skrypt (requests) by tego nie zrobił, bo strona wymaga sesji i kliknięć.

Selenium zrobi to za Ciebie w 5 sekund.

Zadanie:
Odpal ten kod. Zobaczysz, że przeglądarka sama wstanie i zacznie napieprzać kliknięcia w ciasteczko.

Co robimy dalej?
W następnych lekcjach Angela będzie pewnie pokazywać jak szukać elementów przez `XPATH`. 
To jest najważniejsza umiejętność w `Selenium`. 
Chcesz, żebym Ci pokazał jak w 3 sekundy wyciągnąć dowolny `XPATH` ze strony, 
żebyś nie musiał zgadywać, co wpisać w find_element?

Lecimy z tym XPATH-em !!


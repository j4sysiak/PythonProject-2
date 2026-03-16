Dzień 38
--------

Day_38_Selenium_bot_w_Google_browser
------------------------------------

Pokażę ci, jak w Selenium obsługiwać "dynamiczne treści"? 
(Np. strony, które ładują się przez 5 sekund po kliknięciu – zwykły kod wtedy rzuca błąd, bo "nie widzi elementu", 
a my użyjemy tzw. `WebDriverWait`, żeby zmusić bota do cierpliwego czekania).

To jest niezbędne w 90% komercyjnych botów.

`WebDriverWait` o jest standardowy element tego kursu w sekcjach o Selenium. 
Bez tego projekty z automatyzacją stron (jak np. projekt z automatycznym kupowaniem produktów lub graniem w gry przeglądarkowe) 
po prostu nie działałyby stabilnie.

Strony internetowe działają asynchronicznie. 
iedy klikasz przycisk "Zaloguj", przeglądarka musi wysłać dane do serwera i dostać odpowiedź – to trwa np. 0.5 sekundy. 
Jeśli Twój skrypt spróbuje kliknąć następny przycisk zanim strona się przeładuje, dostaniesz błąd `NoSuchElementException`.

Mamy 2 podejścia do tego problemu:
----------------------------------

1. `Implicit Wait` (driver.implicitly_wait(10)): 
    To jest "tępe" czekanie. 
    Mówisz robotowi: "Jak nie widzisz elementu, czekaj do 10 sekund". 
    To proste, ale mało precyzyjne.

2. `Explicit Wait` (WebDriverWait): 
    To jest "mądre" czekanie. 
    Mówisz: "Czekaj, aż przycisk o ID 'submit' stanie się klikalny, ale nie dłużej niż 10 sekund".

Jak to może wyglądać w kodzie (Inżynieria):

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Czekaj maksymalnie 10 sekund, aż element będzie obecny w DOM strony
element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "my-dynamic-element"))
)
element.click()
```

Co tu się dzieje:
-----------------

expected_conditions (EC): 
To jest zestaw gotowych warunków. 
Możesz czekać aż element będzie: 
  - widoczny
  - klikalny
  - obecny w kodzie HTML
  - aż zniknie

until: 
To jest "pętla" wewnątrz biblioteki. 
Ona co ułamek sekundy sprawdza: "Czy już jest? A teraz? A teraz?". 
Jeśli po 10 sekundach nie będzie – rzuca błąd.

Dlaczego to jest ważne dla Ciebie?
W Twojej firmie na pewno są systemy webowe, które "zamulają" albo ładują się długo. 
Używając `WebDriverWait`, Twój bot będzie "cierpliwy". 
Będzie czekał dokładnie tyle, ile potrzeba, a jak tylko strona się załaduje – w ułamku sekundy wykona robotę.


Zadanie-1
---------

Pokażę Ci teraz "Złoty Standard" Selenium. 
W pracy nigdy nie używa się `sleep()` ani `implicitly_wait()`. 
Używa się `WebDriverWait`, bo tylko to daje gwarancję, że bot nie wywali się w połowie roboty przez wolny internet.

Wyobraź sobie, że musisz automatycznie zalogować się do systemu firmowego. 
Oto jak to się pisze profesjonalnie, żeby było odporne na zmulone ładowanie stron:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. Konfiguracja (Chrome w trybie "roboczym")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.google.com") # Przykładowa strona

# 2. Mechanizm "Czekaj, aż będzie gotowe" (to jest to, co Angela nazywa trudnym, a co jest fundamentem)
wait = WebDriverWait(driver, 10) # Maksymalnie 10 sekund cierpliwości

try:
    # Czekaj, aż pole wyszukiwania będzie możliwe do kliknięcia (clickable)
    # Zamiast "sleep(5)", bot sprawdza co 0.5s: "Czy już mogę tu pisać?"
    search_box = wait.until(EC.element_to_be_clickable((By.NAME, "q")))
    
    # 3. Akcja
    search_box.send_keys("Automatyzacja procesów Python")
    search_box.submit()
    
    print("Zadanie wykonane poprawnie.")

except Exception as e:
    print(f"Błąd! Strona nie załadowała się w czasie lub element nie istnieje: {e}")

finally:
    # Zawsze zamykamy po zakończeniu, niezależnie czy był błąd czy nie
    # driver.quit() 
    pass
```

Co tu jest najważniejsze dla Ciebie (inżyniera):

EC.element_to_be_clickable: 
To jest "bóg" automatyzacji. 
Nie sprawdzasz, czy element istnieje (bo może istnieć, ale być przykryty innym oknem ładowania). 
Sprawdzasz, czy jest klikalny.

try...except: 
To jest Twoja polisa ubezpieczeniowa. 
Jeśli serwer Twojej firmy padnie, skrypt nie "zdechnie" w konsoli, tylko wypluje błąd w logach, który Ty sobie przeczytasz rano.

driver.get() / send_keys() / submit(): 
To jest zestaw narzędzi do przejęcia kontroli nad przeglądarką.



Zadanie-2:
----------

Zrobimy teraz bota, który:
1. Otwiera Google.
2. Czeka, aż pole wyszukiwania stanie się aktywne.
3. Wpisuje "Automatyzacja procesów".
4. Fizycznie klika przycisk "Szukaj w Google" (zamiast używać Entera), żebyś zobaczył, że potrafimy przejmować kontrolę nad interfejsem.


Kod bota (Wklej do main.py w projekcie Day_36_Selenium):

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 1. Odpalamy przeglądarkę
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
driver.get("https://www.google.com")

# 2. Cierpliwy Czekacz (WebDriverWait) - to jest fundament stabilności
wait = WebDriverWait(driver, 10)

try:
    # Akceptujemy cookies jeśli się pojawią (często wyskakują na starcie)
    # Znajdujemy przycisk "Zaakceptuj wszystko" po XPATH
    accept_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Zaakceptuj')]")))
    accept_button.click()
    print("Cookies zaakceptowane.")

except:
    print("Brak cookies lub inne okno startowe.")

# 3. Pole wyszukiwania
search_box = wait.until(EC.element_to_be_clickable((By.NAME, "q")))
search_box.send_keys("Automatyzacja procesów Python")

# 4. KLUCZOWY MOMENT: Przejęcie przycisku "Szukaj w Google"
# Czekamy, aż przycisk pojawi się pod polem tekstowym i stanie się klikalny
search_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnK")))
search_button.click()

print("Przycisk kliknięty. Bot wykonał robotę.")
```

Co tu jest ważne dla Ciebie jako inżyniera:

Dlaczego try/except przy cookies? 
Bo strony mają różny "start". 
Czasem Google pokazuje cookies, czasem nie. 
Gdybyś nie dał try/except przy akceptacji ciasteczek, program wywaliłby błąd, gdyby ich nie było. 
Tak traktujesz błąd jako "informację" i idziesz dalej.

By.NAME, "btnK": 
Google ma bardzo przewidywalne nazwy elementów. q to pole wyszukiwania, a btnK to przycisk "Szukaj w Google".

By.XPATH z contains: 
To jest pro-tip. //button[contains(., 'Zaakceptuj')] oznacza: "Znajdź mi dowolny przycisk na stronie, który w swojej treści zawiera słowo 'Zaakceptuj'". 
Dzięki temu nie musisz szukać ID czy klasy – bot czyta stronę tak jak Ty.

Jak to przetestować:
Odpal to.
Zobaczysz, jak w ułamku sekundy akceptuje ciasteczka.
Wpisuje frazę.
Zatrzyma się na sekundę (żebyś widział, że pole jest aktywne).
Kliknie w przycisk "Szukaj w Google" i przeładuje stronę z wynikami.

Jeśli to zadziała, to znaczy, że masz pełną kontrolę. 
Czy bot kliknął w przycisk? 
Jeśli tak, to znaczy, że jesteś gotowy na kolejny poziom – czyli podpięcie tego pod Twoje zadania w firmie.

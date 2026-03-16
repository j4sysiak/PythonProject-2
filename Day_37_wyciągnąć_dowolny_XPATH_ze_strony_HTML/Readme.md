Dzień 37
--------

Day_37_wyciągnąć_dowolny_XPATH_ze_strony_HTML
---------------------------------------------


Jak w 3 sekundy wyciągnąć dowolny XPATH ze strony, żebyś nie musiał zgadywać, 
co wpisać w find_element? 
Jeśli tak, to lecimy z tym XPATH-em czy chcesz jeszcze coś innego z tego zakresu?


Zapomnij o zgadywaniu. 
Nie musisz uczyć się składni XPATH na pamięć, żeby z niego korzystać. 
Każda współczesna przeglądarka (Chrome, Edge, Firefox) ma wbudowane narzędzie "Kopiuj XPATH".

Oto jak to zrobić "po męsku", w 5 sekund, bez czytania dokumentacji:

1. Otwórz Narzędzia Deweloperskie (DevTools)

Wejdź na stronę, z której chcesz wyciągnąć dane.

Kliknij prawym przyciskiem myszy na element, który Cię interesuje (np. przycisk "Zaloguj" albo cenę produktu).

Wybierz Zbadaj (Inspect).

2. Wyciągnij XPATH

W oknie po prawej (lub na dole) podświetli się konkretna linijka kodu HTML.

Kliknij na tę podświetloną linijkę prawym przyciskiem myszy.

Najedź na Copy.

Wybierz Copy XPath.

Gotowe. Do schowka trafił ciąg znaków typu: //*[@id="login-button"] albo /html/body/div[2]/div/form/button.

Jak tego użyć w Pythonie (Selenium)?

Kiedy masz już ten XPATH w schowku, wrzucasz go do swojego kodu:

```python
from selenium.webdriver.common.by import By

# Wklejasz to, co skopiowałeś z przeglądarki
element = driver.find_element(By.XPATH, value='//*[@id="login-button"]')
element.click()
```

Pułapka, o której musisz wiedzieć (Inżynieryjny pro-tip)

Przeglądarka kopiuje tzw. "Pełny XPATH" (np. /html/body/div[2]/div/form/div/button) - To jest zło.
Dlaczego? Bo jeśli programista strony doda choć jeden <div> na górze strony, Twój XPATH przestanie działać i robot się wywali.

Rób tak:
Szukaj XPATH-a, który używa unikalnych atrybutów. 
Jeśli możesz, używaj `By.ID` lub `By.CSS_SELECTOR` (np. By.CSS_SELECTOR, "#login-button").

Jeśli jednak musisz użyć XPATH (bo element nie ma ID ani klasy), to staraj się go skrócić do czegoś unikalnego. Przykład:

Pełny (zły): /html/body/div[1]/div[2]/form/div/input

Względny (lepszy): //form//input[@name='username']

Jak napisać taki "względny" XPATH?
Dopisujesz ręcznie: //tag[@atrybut='wartość'].
To mówi robotowi: "Szukaj gdziekolwiek (//) tagu input, który ma atrybut name równy username".

Dzięki temu, nawet jak zmieni się cała struktura strony, Twój robot nadal trafi w odpowiednie pole.

Co teraz?

Masz już Selenium, masz "wędkę" (XPATH), żeby łowić elementy na każdej stronie w internecie.

Co robimy w następnym kroku?
Czy chcesz, żebym Ci pokazał jak w Selenium obsługiwać "dynamiczne treści"? 
(Np. strony, które ładują się przez 5 sekund po kliknięciu – zwykły kod wtedy rzuca błąd, bo "nie widzi elementu", 
a my użyjemy tzw. `WebDriverWait`, żeby zmusić bota do cierpliwego czekania).

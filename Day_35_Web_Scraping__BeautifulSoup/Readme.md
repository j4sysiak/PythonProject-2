Dzień 35
--------

Day_35_Web_Scraping__BeautifulSoup
----------------------------------
 
Skoro masz już API, to wiesz, że dane przychodzą do Ciebie ładnie zapakowane w JSON. 
Ale co jeśli chcesz wyciągnąć cenę produktu z Allegro, której nie ma w API? 
Musisz "ukraść" te dane bezpośrednio z HTML-a strony.

Narzędzia (po męsku):

BeautifulSoup: 
Parser, który zmienia kod strony HTML w drzewo obiektów, po którym możesz chodzić (znajdź mi <h1>, znajdź mi <a> z klasą price).

requests: 
To już znasz – pobiera kod strony tak, jakbyś wszedł w przeglądarce i zrobił "Pokaż źródło strony".

Instalacja:

W terminalu:
`pip install beautifulsoup4`
(Sam requests już masz z poprzedniego dnia).

Pierwszy projekt: 
Skrobanie nagłówków z "Hacker News"

Hacker News to najpopularniejszy portal dla programistów na świecie. 
Zrobimy skrypt, który wyciąga najpopularniejszy artykuł dnia.

Stwórz projekt Day_35_WebScraping, plik main.py i wklej to:

```python
from bs4 import BeautifulSoup
import requests

# 1. Pobieramy cały kod HTML strony
response = requests.get("https://news.ycombinator.com/")
yc_web_page = response.text

# 2. Tworzymy obiekt "zupy" (BeautifulSoup), który przetrawi ten kod
soup = BeautifulSoup(yc_web_page, "html.parser")

# 3. Wyciągamy wszystkie tytuły (w HTML Hacker News są w tagach <span class="titleline">)
articles = soup.find_all(name="span", class_="titleline")

# 4. Wyciągamy pierwszy artykuł (nazwa + link)
first_article = articles[0]
article_text = first_article.getText()
article_link = first_article.find("a").get("href")

print(f"Najpopularniejszy artykuł: {article_text}")
print(f"Link: {article_link}")
```

Co tu jest najważniejsze (Inżynieria):
`soup.find_all(name="tag", class_="klasa")`: 
To jest serce web scrapingu. 
Strona WWW to gąszcz znaczników. 
Ty mówisz: "daj mi wszystkie elementy span z klasą titleline".

getText() i get("href"): 
Po znalezieniu elementu HTML wyciągasz z niego to, co Cię interesuje – albo czysty tekst, albo konkretny atrybut (np. link w href).

Analiza strony (F12): 
W prawdziwej pracy nie zgadujesz nazw klas. 
Klikasz prawym przyciskiem myszy na interesujący Cię element na stronie -> "Zbadaj" (Inspect). 
Patrzysz, jaki ma tag i klasę, i dokładnie to wpisujesz w `find_all`.

To jest ten moment, kiedy Twoje możliwości są nieograniczone. 
Jeśli strona nie ma zabezpieczeń typu "anty-bot", możesz stamtąd wyciągnąć dowolną informację.

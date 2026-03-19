Dzień 52
--------

Day_52_Portfolio_Webowe_Boty__Job_Automation_DataEntry
------------------------------------------------------

To jest różnicę między "klepaczem w Excelu" a "Inżynierem Automatyzacji".

Scenariusz biznesowy:
---------------------

Twój szef przychodzi do Ciebie i mówi: 
Tu jest strona z setką ofert wynajmu mieszkań. 
Proszę mi to do jutra przepisać do naszego firmowego Excela (adres, cena, link)."

Piszesz skrypt, który:
1. Wchodzi na stronę.
2. W ułamku sekundy kradnie wszystkie dane (Web Scraping / BeautifulSoup).
3. Otwiera przeglądarkę (Selenium).
4. Samodzielnie, na Twoich oczach, wypełnia formularz 100 razy z rzędu z prędkością karabinu maszynowego, wysyłając dane prosto do Twojego Arkusza Google.

Krok 1: Przygotowanie poligonu (Formularz)
-----------------------------------------

Wejdź naGoogle Forms (Formularze Google) i stwórz nowy, pusty formularz.
Dodaj dokładnie 3 pytania typu "Krótka odpowiedź" (Short answer). 
Nazwij je kolejno:
 - Adres
 - Cena
 - Link

Kliknij "Wyślij" w prawym górnym rogu, skopiuj link do tego formularza i wklej go do kodu poniżej w zmienną FORM_URL.

`https://docs.google.com/forms/d/e/1FAIpQLSfrGNw25LWXlGNUKgnttk31TN-YIOgkKb76nKTpELEBagvnVw/viewform`


(Gdy skrypt skończy pracę, w formularzu Google klikniesz zakładkę "Odpowiedzi" -> "Utwórz arkusz" i masz gotowego Excela dla szefa).

Krok 2: Kod (Czysta Inżynieria)
-------------------------------

Żebyśmy nie walczyli z zabezpieczeniami anty-botowymi (Captcha), 
użyjemy specjalnego klonu strony z nieruchomościami przygotowanego przez Angelę na GitHubie. 
Zawsze działa i ma stabilny kod HTML.

Wklej to do main.py:

```python
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

# --- KONFIGURACJA ---
# TUTAJ WKLEJ LINK DO SWOJEGO FORMULARZA GOOGLE!
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfrGNw25LWXlGNUKgnttk31TN-YIOgkKb76nKTpELEBagvnVw/viewform"
ZILLOW_CLONE_URL = "https://appbrewery.github.io/Zillow-Clone/"

print("Rozpoczynam kradzież danych ze strony...")

# ==========================================
# 1. WEB SCRAPING (Wciągamy dane z sieci)
# ==========================================
response = requests.get(ZILLOW_CLONE_URL)
soup = BeautifulSoup(response.text, "html.parser")

# Wyciągamy wszystkie linki do ofert
link_elements = soup.select(".StyledPropertyCardDataArea-anchor")
all_links = [link["href"] for link in link_elements]

# Wyciągamy wszystkie adresy
address_elements = soup.select("address")
all_addresses =[address.text.strip().replace(" | ", " ") for address in address_elements]

# Wyciągamy wszystkie ceny (i czyścimy je z syfu typu "/mo" czy "+ 1bd")
price_elements = soup.select(".PropertyCardWrapper span")
all_prices = [price.text.strip().replace("/mo", "").split("+")[0] for price in price_elements]

print(f"Pobrano {len(all_links)} ofert. Odpalam robota do wprowadzania danych!")

# ==========================================
# 2. SELENIUM AUTOMATION (Wpisujemy dane do Formularza)
# ==========================================
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

# Pętla przelatuje przez wszystkie pobrane oferty
for n in range(len(all_links)):
    # 1. Bot otwiera Twój formularz Google
    driver.get(FORM_URL)
    
    # Dajemy formularzowi 2 sekundy na załadowanie elementów (żeby uniknąć błędów)
    time.sleep(2)
    
    # 2. Szukamy wszystkich 3 pól tekstowych (Google Forms używa input type="text")
    # Zwraca listę 3 elementów!
    inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
    
    # 3. Wpisujemy dane symulując klawiaturę
    inputs[0].send_keys(all_addresses[n])
    inputs[1].send_keys(all_prices[n])
    inputs[2].send_keys(all_links[n])
    
    # 4. Szukamy przycisku "Wyślij" (Google Forms używa div z role="button")
    submit_button = driver.find_element(By.CSS_SELECTOR, "div[role='button']")
    submit_button.click()
    
    print(f"Wysłano ofertę {n+1}/{len(all_links)}")

print("Robota skończona. Szefie, Excel gotowy.")
driver.quit() # Zamykamy przeglądarkę
```

Co tu się dzieje pod maską (Inżynieria):
---------------------------------------

soup.select(): 
To jest potęga CSS Selectorów. 
Zamiast bawić się w szukanie pojedynczych tagów, używasz kropki (.klasa), żeby wyciągnąć dokładnie to, co chcesz. 
W prawdziwej pracy klikasz F12 (Zbadaj element), patrzysz jaką klasę ma cena, i wpisujesz ją w select().

Czyszczenie danych (Data Cleaning): 
Zauważ linijkę z cenami: `.replace("/mo", "").split("+")[0]`. 
Strony WWW to śmietnik. 
Jedna cena to $3,000/mo, inna to $2,500+ 1bd. 
Ten krótki łańcuch komend czyści wszystko do gołych liczb. Zawsze czyść dane przed wsadzeniem ich do `bazy/formularza`.

driver.find_elements (z 's' na końcu): 
To jest genialny trik. 
Skoro wiemy, że formularz ma 3 pola tekstowe, nie musimy szukać XPATH-a każdego z osobna. 
Pobieramy je jako listę (inputs) i odwołujemy się przez indeksy: 
 - `inputs[0] to adres`
 - `inputs[1] to cena`
 - `inputs[2] to link`

Przetestuj to:

Odpal ten skrypt, odłóż ręce od klawiatury i patrz na ekran. 
Zobaczysz, jak przeglądarka sama wstaje, ładuje Twój formularz, wklepuje dane, klika wyślij, klika "Prześlij kolejną odpowiedź" i tak w kółko,
aż przetworzy kilkadziesiąt ofert.

Jak skończy – wejdź na swojego Google Drive, otwórz odpowiedzi z formularza i wygeneruj Arkusz Google (Excel).

Widzisz to? Właśnie zautomatyzowałeś 5 godzin nudnej, biurowej roboty do 3 minut. To jest moment, za który płaci się w IT grube pieniądze. Daj znać, jak robot skończy klepać!




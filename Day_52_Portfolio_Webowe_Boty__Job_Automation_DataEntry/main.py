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
all_links = [link["href"] for link in link_elements]  # Linia 22 to list comprehension, które iteruje po liście link_elements (elementów HTML <a>) i z każdego wyciąga wartość atrybutu href (czyli adres URL linku).

# Wyciągamy wszystkie adresy
address_elements = soup.select("address")
all_addresses = [address.text.strip().replace(" | ", " ") for address in address_elements]

# Wyciągamy wszystkie ceny (i czyścimy je z syfu typu "/mo" czy "+ 1bd")
price_elements = soup.select(".PropertyCardWrapper span")
all_prices = [price.text.strip().replace("/mo", "").split("+")[0] for price in price_elements]

print(f"Pobrano {len(all_links)} ofert. Odpalam robota do wprowadzania danych!")

# =====================================================
# 2. SELENIUM AUTOMATION (Wpisujemy dane do Formularza)
# =====================================================
chrome_options = webdriver.ChromeOptions()  # Tworzy obiekt konfiguracji przeglądarki Chrome dla Selenium. Utworzony obiekt chrome_options jest później przekazywany do webdriver.Chrome(options=chrome_options) w linii 39, aby przeglądarka uruchomiła się z tymi ustawieniami.
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

# Pętla przelatuje przez wszystkie pobrane oferty
for n in range(len(all_links)):
    # 1. Bot otwiera Twój formularz Google
    # ta linia nakazuje przeglądarce Chrome (sterowanej przez Selenium)
    # przejść pod adres URL zapisany w zmiennej FORM_URL, czyli otworzyć formularz Google Forms.
    driver.get(FORM_URL)

    # Dajemy formularzowi 2 sekundy na załadowanie elementów (żeby uniknąć błędów)
    time.sleep(2)

    # 2. Szukamy wszystkich 3 pól tekstowych (Google Forms używa input type="text")
    # Zwraca listę 3 elementów!
    # Metoda find_elements (liczba mnoga) zwraca listę wszystkich elementów HTML pasujących do selektora CSS.
    # W tym przypadku selektor "input[type='text']" wyszukuje na stronie formularza Google wszystkie pola tekstowe (<input type="text">). Formularz Google Forms ma 3 pytania tekstowe (cena, link, adres), więc:
    # inputs[0] → pierwsze pole (cena)
    # inputs[1] → drugie pole (link)
    # inputs[2] → trzecie pole (adres)
    # To jest standardowa lista Pythona (list[WebElement]), dlatego w liniach 56–58 można się do poszczególnych pól odwoływać po indeksie.
    inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")

    # 3. Wpisujemy dane symulując klawiaturę
    inputs[0].send_keys(all_prices[n])
    inputs[1].send_keys( all_links[n])
    inputs[2].send_keys(all_addresses[n])

    # 4. Szukamy przycisku "Wyślij" (Google Forms używa div z role="button")
    submit_button = driver.find_element(By.CSS_SELECTOR, "div[role='button']")
    submit_button.click()

    print(f"Wysłano ofertę {n + 1}/{len(all_links)}")

print("Robota skończona. Wszystkie oferty wysłane do Google Forms.")
driver.quit()  # Zamykamy przeglądarkę

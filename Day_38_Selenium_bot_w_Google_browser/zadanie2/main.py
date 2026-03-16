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
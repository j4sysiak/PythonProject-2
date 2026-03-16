from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# 1. Inicjalizacja przeglądarki (Chrome)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)  # Żeby okno nie zamykało się od razu
driver = webdriver.Chrome(options=chrome_options)

# 2. Otwieramy stronę
driver.get("http://orteil.dashnet.org/experiments/cookie/")

# 3. Znajdź ciasteczko (element z ID "cookie")
cookie = driver.find_element(By.ID, value="cookie")

# 4. Pętla klikania przez 5 sekund
timeout = time.time() + 5
while time.sleep(0.01) is None:  # Trik na nieskończoną pętlę
    cookie.click()

    # Warunek wyjścia z pętli po 5 sekundach
    if time.time() > timeout:
        break

driver.quit() # Odkomentuj to, jeśli chcesz, żeby robot zamykał okno po zakończeniu
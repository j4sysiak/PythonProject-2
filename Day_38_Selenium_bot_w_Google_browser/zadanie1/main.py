from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. Konfiguracja (Chrome w trybie "roboczym")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.google.com")  # Przykładowa strona

# 2. Mechanizm "Czekaj, aż będzie gotowe" (to jest to, co Angela nazywa trudnym, a co jest fundamentem)
wait = WebDriverWait(driver, 10)  # Maksymalnie 10 sekund cierpliwości

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
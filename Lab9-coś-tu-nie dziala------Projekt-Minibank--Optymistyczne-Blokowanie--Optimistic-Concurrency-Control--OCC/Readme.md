Lab9
----

Lab9--Projekt-Minibank--Optymistyczne-Blokowanie--Optimistic-Concurrency-Control--OCC
-------------------------------------------------------------------------------------
Wchodzimy w tryb High-Concurrency Finance.
Blokada pesymistyczna (FOR UPDATE) to "kłódka" na wierszu w bazie – jak jeden wątek czyta, drugi musi czekać.
Blokada optymistyczna (OCC) to zakład wiersza o wersję.
Jeśli podczas transakcji wiersz w bazie zmienił wersję (ktoś inny coś zapisał), Twój zapis się nie uda. 
To jest ultra-szybkie w systemach, gdzie rzadko zdarzają się konflikty, ale musimy mieć 100% pewność danych.
Zrobimy to w trzech krokach: Model, Logika, Test.

Skoro masz już testy (Twoja siatka bezpieczeństwa świeci się na zielono), możemy "rozpruć" główny silnik bazy danych bez strachu.
Dlaczego to robimy? (Teoria Architekta)
Twoja obecna blokada pesymistyczna (`.with_for_update()`) działa świetnie, ale ma jedną wadę: 
  - zabija wydajność przy gigantycznym ruchu
  - blokuje wiersze w bazie na czas całej transakcji (odczyt -> API Walut -> obliczenia -> zapis) więc inne przelewy muszą czekać w kolejce

Blokada Optymistyczna zakłada, że konflikty są rzadkie.
Odczytujemy dane (wersja = 1).
Sprawdzamy kursy walut i liczymy wszystko w pamięci RAM (baza nie jest zablokowana, inni mogą czytać!).
Przy zapisie (COMMIT) wysyłamy komendę: "Zmień saldo na X, ALE TYLKO JEŚLI wersja w bazie to nadal 1".
Jeśli w międzyczasie ktoś inny zdążył zmienić saldo (wersja w bazie to już 2), baza odrzuci nasz zapis, 
a SQLAlchemy rzuci błąd `StaleDataError`.
W Springu robi się to adnotacją `@Version`. 
W Pythonie to kwestia dodania jednego słownika do modelu.


Krok 1: Włączenie @Version w bazie (models.py)
----------------------------------------------
Pamiętasz, że w Labie 2 zapobiegawczo dodaliśmy już kolumnę `version` do klasy Account? 
Teraz musimy powiedzieć SQLAlchemy, żeby faktycznie zaczęło jej używać jako mechanizmu blokad.

Otwórz `models.py` i dodaj zmienną `__mapper_args__` na samym dole klasy Account:

```python
# models.py
# (upewnij się, że masz zaimportowany Integer)

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_name: Mapped[str] = mapped_column(String(100), nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")

    # Pole do blokad optymistycznych (@Version ze Springa)
    version: Mapped[int] = mapped_column(Integer, default=1)

    # --- TO JEST ODPOWIEDNIK @Version ze Springa ---
    __mapper_args__ = {
        "version_id_col": version # SQLAlchemy będzie pilnować tego pola!
    }
```

Dzięki temu `SQLAlchemy` samo będzie podbijać kolumnę version (+1) przy każdym UPDATE 
i automatycznie sprawdzać konflikty.

Krok 2: Usunięcie pesymistycznej blokady i obsługa konfliktów (main.py)
-----------------------------------------------------------------------
Teraz przebudujemy endpointy:
  1. przelewu (`/convert-transfer`)
  2. transferu (`/transfer`) 
  3. transaction (`/transaction`)


Wywalamy `.with_for_update()`, żeby nie blokować bazy.
Teraz bazujemy na tym, że jeśli wersja się nie zgadza przy commit(), `SQLAlchemy` automatycznie rzuci `StaleDataError`.
Dodajemy obsługę błędu `StaleDataError`, zwracając status 409 Conflict (Standard REST, 
gdy dwa systemy próbują edytować ten sam zasób).

Otwórz `main.py`, zmodyfikuj endpointy 
pod kątem usunięcia `.with_for_update()` i dodania obsługi `StaleDataError`:
 - `/transfer`
 - `/transaction`
 - `/convert-transfer`


```python
# Dodaj w sekcji importów na górze main.py:
from sqlalchemy.orm.exc import StaleDataError

# ... (zmodyfikowane wszystkie edpointy finansowe: transfer, transaction and convert-transfer) ...
```


Krok 3: Udowodnienie, że to działa (Test Obciążeniowy)
------------------------------------------------------
Zapisz pliki (Docker się zrestartuje).
Wyzeruj stan: 
ustaw sobie w Swaggerze na Koncie A 100 PLN.

Odpal znowu skrypt `load_test.py` (ten, który atakuje 50 wątkami na raz w jednej milisekundzie).

Czego oczekujemy?
Przy blokadzie pesymistycznej miałeś: 10 x OK (200) i 40 x Brak Środków (400).
Przy blokadzie optymistycznej, ponieważ nie blokujemy bazy na odczyt, 
wszystkie 50 wątków wejdzie do funkcji w ułamku sekundy. 
Wszystkie przeczytają wersję 1 i saldo 100 zł.

Tylko pierwszy wątek zdoła zrobić COMMIT. 
Pozostałe wątki spróbują zapisać dane, ale wersja w bazie będzie już wynosić 2.
W efekcie powinieneś zobaczyć w podsumowaniu testu statusy 409 Conflict!

Oto dowód, że serwer działa na pełnej prędkości (bez kolejkowania sprzętowego bazy), 
ale integralność (ACID) została nienaruszona. 
W prawdziwym świecie na Froncie (w Angularze) łapiesz błąd 409 i robisz niejawny retry 3 razy, zanim pokażesz błąd użytkownikowi.

Odpal test obciążeniowy i sprawdź, czy pojawiły się HTTP 409! Daj znać!
 


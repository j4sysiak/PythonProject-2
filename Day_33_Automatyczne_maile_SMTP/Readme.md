Dzień 33
--------

Day_33_Automatyczne_maile_SMTP
------------------------------

W Dniu 33 Angela łączy API z wysyłaniem maili. 
Używamy biblioteki `smtplib` (wbudowana w Pythona).

Uwaga: Jeśli używasz Gmaila, musisz wygenerować "App Password" (Hasło aplikacji) w ustawieniach konta Google, 
bo zwykłe hasło do logowania nie zadziała ze względów bezpieczeństwa.

```python
import smtplib

my_email = "j4sysiak@gmail.com"
password = "???????????????" # Nie zwykłe hasło!

# 1. Łączymy się z serwerem SMTP Gmaila
with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
    connection.starttls() # Zabezpieczamy połączenie (szyfrowanie)
    connection.login(user=my_email, password=password)
    
    # 2. Wysyłamy maila
    connection.sendmail(
        from_addr=my_email,
        to_addrs="CEL@gmail.com",
        msg="Subject:Hello!\n\nTo jest testowy mail wysłany z Pythona."
    )
```

Co tu jest najważniejsze:

starttls(): 
To szyfrowanie. 
Bez tego wysyłałbyś hasło do maila otwartym tekstem przez internet – każdy w sieci mógłby je przechwycić.

Format wiadomości: 
`Subject:Hello!\n\nTreść`. 
Musisz dać dwa entery (\n\n) po temacie, żeby serwer wiedział, gdzie kończy się temat, a zaczyna treść maila.

Co teraz?
Masz już narzędzia, żeby:
1. Pobrać dane z internetu (API). 
2. Przetworzyć je (Pandas/JSON). 
3. Wysłać powiadomienie (Email).

To jest kompletny zestaw do budowania botów. 
Możesz teraz napisać skrypt, który co 5 minut sprawdza cenę Bitcoina albo pogodę, i wysyła Ci maila, jak cena spadnie poniżej X.




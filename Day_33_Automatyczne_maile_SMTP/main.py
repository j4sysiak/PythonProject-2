import smtplib

my_email = "j4sysiak@gmail.com"
password = "???????????????????" # Nie zwykłe hasło!

# 1. Łączymy się z serwerem SMTP Gmaila
with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
    connection.starttls()  # Zabezpieczamy połączenie (szyfrowanie)
    connection.login(user=my_email, password=password)

    # 2. Wysyłamy maila
    msg = f"Subject:Hello!\n\nTo jest testowy mail wysłany z Pythona."
    connection.sendmail(
        from_addr=my_email,
        to_addrs="j4sysiak@gmail.com",
        msg=msg.encode('utf-8')
    )
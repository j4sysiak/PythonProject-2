Motywem przewodnim Dnia 17 jest tworzenie własnych klas od zera (Custom Classes) oraz używanie konstruktora (__init__).
To przejście od bycia "użytkownikiem" obiektów do bycia ich "twórcą".

Żeby to dobrze zrozumieć, spójrz na różnicę:

W Dniu 16 uczyłeś się, jak używać gotowych klas. 
Ktoś inny (w tym wypadku Angela) napisał kod ekspresu do kawy, a Ty tylko tworzyłeś z niego obiekt 
i odpalałeś gotowe komendy (np. coffee_maker.report()). 
Byłeś jak kierowca, który wsiada do auta i po prostu wciska gaz.

W Dniu 17 stajesz się inżynierem. 
Uczysz się, jak samodzielnie zaprojektować taki szablon od zera.

Najważniejsze rzeczy, które Angela wałkuje w tym dniu, to:

Słowo kluczowe class: 
Jak w ogóle zdefiniować nowy typ obiektu (np. class Question:).

Konstruktor __init__: 
To ta dziwna funkcja z podłogami, którą widziałeś w kodzie. 
To jest "funkcja startowa". 
Odpala się automatycznie w ułamku sekundy, gdy tylko tworzysz nowy obiekt. 
Służy do tego, żeby nadać obiektowi początkowe cechy (np. przypisać mu tekst pytania i odpowiedź).

Słowo self: 
Zrozumienie, że self to po prostu odniesienie do "samego siebie" (konkretnego obiektu, na którym w danej chwili pracujesz).

Współpraca obiektów: 
Przekazywanie jednych obiektów do drugich. 
Zauważ, że w `main.py` stworzyliśmy listę obiektów `Question` i wsadziliśmy ją w całości do "mózgu" gry, czyli obiektu `QuizBrain`.
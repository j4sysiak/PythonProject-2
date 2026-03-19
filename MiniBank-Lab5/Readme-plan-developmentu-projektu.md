

LAB 5: Opcja B – Integracja z Twoim Angularowym Frontendem (CORS)

Skoro znasz Angulara, nie ma sensu budować frontu w Jinja.

Dlaczego: Musisz umieć podpiąć swoje API (FastAPI) pod prawdziwy, nowoczesny frontend (Angular). To jest praca, którą wykonuje każdy Fullstack codziennie: "jak połączyć backend z tym, co widzi user?".

LAB 6: Opcja E – Testy Jednostkowe i Integracyjne (Pytest + Testcontainers)

W Springu masz @SpringBootTest i Testcontainers. W Pythonie musisz umieć to samo.

Dlaczego: Bez testów, nikt nie wpuści Twojego kodu na serwer produkcyjny. Napiszemy testy, które w locie stawiają "bazę w kontenerze", wykonują przelew i sprawdzają, czy saldo się zgadza. To jest to, czego boi się większość Pythonowców, a co dla Ciebie (po Javie) będzie naturalne.

LAB 7: Opcja N – CI/CD (GitHub Actions + Docker Hub)

Na koniec zrobimy profesjonalny proces wdrożeniowy.

Dlaczego: Za każdym razem, gdy zrobisz git push, GitHub Actions automatycznie uruchomi Twoje testy z LAB-a 6, zbuduje nowy obraz Dockerowy i wypchnie go na Docker Hub. To jest standard w 2026 roku.

Zaczynamy teraz: LAB 4 (Historia Transakcji i ACID)

Wracamy do Twojego main.py i models.py. Skoro już wiesz, jak to zrobić, zróbmy to porządnie.

Twoje zadanie:

Stwórz tabelę TransactionHistory (id, from_account, to_account, amount, timestamp).

Zaktualizuj endpoint /transfer.

Zasada: Cały proces (odjęcie środków, dodanie środków, zapis do historii) musi być w jednym bloku try...except, kończącym się db.commit() albo db.rollback().

Czy wklejasz kod, czy mam Ci przygotować gotowca do wklejenia, żebyśmy przeszli do Lab 5 (Angular)? Wybierz, jak szybko chcesz to "przeskoczyć".



----------------------------------
Lab5:
Opcja A: Historia Transakcji (Wielowątkowy ACID)
------------------------------------------------
Przelew to nie tylko zmiana salda. 
To też zapis w historii. 
Dodamy tabelę TransactionHistory. 
Nauczysz się, jak w SQLAlchemy w ramach jednej transakcji zmienić saldo dwóch kont ORAZ zapisać rekord historii. 
Jeśli cokolwiek wywali błąd (np. brak prądu), baza musi wycofać (rollback) i salda, i historię.



Lab6:
Opcja B: Połączenie z Frontendem (CORS + Angular)
-------------------------------------------------
Skoro znasz Angulara, na pewno wiesz, co to błąd CORS (Cross-Origin Resource Sharing). 
Skonfigurujemy FastAPI tak, żeby wpuszczał zapytania z Twojego lokalnego środowiska Angularowego (np. localhost:4200), 
żebyś mógł dorobić do tego własny interfejs.


Lab7:
Opcja C: Optymistyczne Blokowanie (@Version)
--------------------------------------------
W modelu daliśmy pole version. 
W systemach o ogromnym natężeniu ruchu blokady pesymistyczne potrafią "zamulić" bazę. 
Pokażę Ci, jak zaimplementować blokadę optymistyczną – nie blokujemy bazy, 
ale przy UPDATE sprawdzamy, czy wersja wiersza się nie zmieniła. Jak się zmieniła -> rzucamy błąd i każemy użytkownikowi spróbować ponownie.




Opcja D: Współbieżność na poziomie aplikacji (Locki w Pythonie)
Opcja E: Testy Jednostkowe i Integracyjne (pytest + Testcontainers)
Opcja F: Docker Compose z Redisem (Cache) i Celery (Asynchroniczne zadania)
Opcja G: Wprowadzenie GraphQL (Ariadne) zamiast REST
Opcja H: Wprowadzenie gRPC (Protobuf) zamiast REST
Opcja I: Wprowadzenie CQRS + Event Sourcing (Kafka + Debezium)
Opcja J: Wprowadzenie Kubernetes (Minikube) do orkiestracji kontenerów
Opcja K: Wprowadzenie DDD (Domain-Driven Design) i Hexagonal Architecture
Opcja L: Wprowadzenie OpenAPI Security (OAuth2 + JWT)
Opcja M: Wprowadzenie Observability (Prometheus + Grafana)
Opcja N: Wprowadzenie CI/CD (GitHub Actions + Docker Hub)
Opcja O: Wprowadzenie Machine Learning (Scikit-learn) do analizy ryzyka kredytowego
Opcja P: Wprowadzenie Blockchain (Ethereum + Solidity) do przelewu międzybankowego
Opcja Q: Wprowadzenie Serverless (AWS Lambda) do obsługi endpointów
Opcja R: Wprowadzenie Microservices (Spring Boot + FastAPI) do rozdzielenia funkcjonalności
Opcja S: Wprowadzenie Event-Driven Architecture (RabbitMQ + FastAPI) do komunikacji między serwisami
Opcja T: Wprowadzenie NoSQL (MongoDB) do przechowywania historii transakcji
Opcja U: Wprowadzenie GraphQL Subscriptions (WebSockets) do powiadomień o nowych transakcjach
Opcja V: Wprowadzenie gRPC Streaming do przesyłania danych o transakcjach w czasie rzeczywistym
Opcja W: Wprowadzenie DDD (Domain-Driven Design) i Hexagonal Architecture
Opcja X: Wprowadzenie OpenAPI Security (OAuth2 + JWT)
Opcja Y: Wprowadzenie Observability (Prometheus + Grafana)
Opcja Z: Wprowadzenie CI/CD (GitHub Actions + Docker Hub) 
Opcja AA: Wprowadzenie Machine Learning (Scikit-learn) do analizy ryzyka kredytowego
Opcja AB: Wprowadzenie Blockchain (Ethereum + Solidity) do przelewu międzybankowego
Opcja AC: Wprowadzenie Serverless (AWS Lambda) do obsługi endpointów
Opcja AD: Wprowadzenie Microservices (Spring Boot + FastAPI) do rozdzielenia funkcjonalności
Opcja AE: Wprowadzenie Event-Driven Architecture (RabbitMQ + FastAPI) do komunikacji między serwisami
Opcja AF: Wprowadzenie NoSQL (MongoDB) do przechowywania historii transakcji
Opcja AG: Wprowadzenie GraphQL Subscriptions (WebSockets) do powiadomień o nowych transakcjach
Opcja AH: Wprowadzenie gRPC Streaming do przesyłania danych o transakcjach w czasie rzeczywistym
Opcja AI: Wprowadzenie AI (ChatGPT API) do obsługi zapytań natural language o saldo i historię transakcji
Opcja AJ: Wprowadzenie Blockchain (Hyperledger Fabric) do przelewu międzybankowego z prywatnymi kanałami
Opcja AK: Wprowadzenie Event Sourcing (EventStoreDB) do zapisywania każdej zmiany stanu jako zdarzenia
Opcja AL: Wprowadzenie CQRS (Command Query Responsibility Segregation) do rozdzielenia operacji zapisu i odczytu
Opcja AM: Wprowadzenie Kubernetes (Minikube) do orkiestracji kontenerów i skalowania aplikacji
Opcja AN: Wprowadzenie Service Mesh (Istio) do zarządzania komunikacją między mikroserwisami
Opcja AO: Wprowadzenie API Gateway (Kong) do zarządzania ruchem i zabezpieczeniami API
Opcja AP: Wprowadzenie Distributed Tracing (Jaeger) do śledzenia przepływu żądań przez system
Opcja AQ: Wprowadzenie Chaos Engineering (Chaos Monkey) do testowania odporności systemu na awarie
Opcja AR: Wprowadzenie Feature Flags (LaunchDarkly) do zarządzania funkcjonalnościami w czasie rzeczywistym
Opcja AS: Wprowadzenie A/B Testing do testowania różnych wersji funkcjonalności i optymalizacji konwersji
Opcja AT: Wprowadenie Blue-Green Deployment do bezpiecznego wdrażania nowych wersji aplikacji bez przerwy dla użytkowników
Opcja AU: Wprowadzenie Canary Releases do stopniowego wdrażania nowych funkcjonalności i monitorowania ich wpływu na system
Opcja AV: Wprowadzenie Serverless Framework do zarządzania funkcjami AWS Lambda i innymi usługami serverless
Opcja AW: Wprowadzenie GraphQL Federation do łączenia wielu serwisów GraphQL w jeden spójny API
Opcja AX: Wprowadzenie gRPC Gateway do automatycznego generowania REST API z serwisu gRPC
Opcja AY: Wprowadzenie OpenAPI Generator do automatycznego generowania klienta API w różnych językach
Opcja AZ: Wprowadzenie Protobuf do definiowania struktur danych i komunikacji między serwisami w sposób wydajny i niezależny od języka programowania
Opcja BA: Wprowadzenie gRPC Reflection do umożliwienia klientom dynamicznego odkrywania dostępnych metod i struktur danych w serwisie gRPC
Opcja BB: Wprowadzenie GraphQL Code Generator do automatycznego generowania typów TypeScript i hooków React z schematu GraphQL
Opcja BC: Wprowadzenie OpenAPI Mock Server do szybkiego prototypowania API i testowania klientów bez konieczności uruchamiania pełnej aplikacji
Opcja BD: Wprowadzenie gRPC Health Checking do monitorowania stanu serwisu gRPC i automatycznego usuwania go z load balancera w przypadku awarii
Opcja BE: Wprowadzenie GraphQL Subscriptions do implementacji powiadomień o nowych transakcjach w czasie rzeczywistym za pomocą WebSockets
Opcja BF: Wprowadzenie gRPC Streaming do przesyłania danych o transakcjach w czasie rzeczywistym, umożliwiając klientom subskrypcję na aktualizacje
Opcja BG: Wprowadzenie AI (ChatGPT API) do obsługi zapytań natural language o saldo i historię transakcji, umożliwiając użytkownikom zadawanie pytań w języku naturalnym i otrzymywanie odpowiedzi w formie tekstowej
Opcja BH: Wprowadzenie Blockchain (Hyperledger Fabric) do przelewu międzybankowego z prywatnymi kanałami, umożliwiając bezpieczne i transparentne przelewy między różnymi instytucjami finansowymi z wykorzystaniem technologii blockchain
Opcja BI: Wprowadzenie Event Sourcing (EventStoreDB) do zapisywania każdej zmiany stanu jako zdarzenia, umożliwiając pełną historię zmian i łatwe odtwarzanie stanu systemu w dowolnym momencie
Opcja BJ: Wprowadzenie CQRS (Command Query Responsibility Segregation) do rozdzielenia operacji zapisu i odczytu, umożliwiając optymalizację wydajności i skalowalności systemu poprzez oddzielenie modeli danych dla operacji zap  


Możemy zrobić Deployment tego banku do Dockera w chmurze (np. na darmowy VPS albo za darmo na platformy typu Render), 
żebyś miał działający w internecie "MiniBank", do którego możesz podpiąć swój Angularowy Frontend.
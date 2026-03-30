# Oficjalny obraz Pythona
FROM python:3.11-slim

# Katalog roboczy w kontenerze
WORKDIR /app

# Kopiujemy plik z zależnościami i instalujemy je
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiujemy resztę kodu
COPY . .

# Wystawiamy port (FastAPI domyślnie działa na 8000)
EXPOSE 8000

# Komenda startowa (odpowiednik java -jar).
# Uvicorn to serwer ASGI (odpowiednik wbudowanego Tomcata/Netty)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
from fastapi import FastAPI

# Inicjalizacja aplikacji
app = FastAPI(
    title="MiniBank API",
    description="System transakcyjny z blokadami optymistycznymi",
    version="1.0.0"
)

# Kontroler (odpowiednik @RestController i @GetMapping)
@app.get("/health")
async def health_check():
    return {"status": "UP", "message": "MiniBank serwer działa poprawnie"}
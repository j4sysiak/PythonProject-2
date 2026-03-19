# schemas.py
from pydantic import BaseModel, Field, ConfigDict

# DTO dla tworzenia konta (Request)
class AccountCreate(BaseModel):
    owner_name: str = Field(..., min_length=2, max_length=100, description="Imię i nazwisko właściciela")
    initial_balance: float = Field(default=0.0, ge=0.0, description="Początkowy depozyt")

# DTO dla zwracania konta (Response)
class AccountResponse(BaseModel):
    id: int
    owner_name: str
    balance: float

    # Pozwala Pydanticowi czytać dane bezpośrednio z obiektów SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
# schemas.py
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal

# DTO dla tworzenia konta (Request)
class AccountCreate(BaseModel):
    owner_name: str = Field(..., min_length=2, max_length=100, description="Imię i nazwisko właściciela")
    initial_balance: Decimal = Field(default=0.0, ge=0.0, description="Początkowy depozyt")
    currency: str = Field(default="PLN", min_length=3, max_length=3) # <--- TO DODAJ do obslugi konwersji walutowych

# klasa DTO dla zwracania konta (Response)
class AccountResponse(BaseModel):
    id: int
    owner_name: str
    balance: Decimal
    currency: str  # <--- TO DODAJ do obslugi konwersji walutowych
    # Pozwala Pydanticowi czytać dane bezpośrednio z obiektów SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


# --- klasa DTO żądania dla transferu
class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: Decimal = Field(..., gt=0.0, description="Kwota musi być większa od zera")


# DTO dla aktualizacji konta (Update)
class AccountUpdate(BaseModel):
    owner_name: str = Field(..., min_length=2, max_length=100, description="Nowe imię i nazwisko właściciela")


from pydantic import BaseModel

class PricingCreate(BaseModel):
    service_type: str
    duration: int
    price: float
    min_persons: int | None = None
    max_persons: int | None = None
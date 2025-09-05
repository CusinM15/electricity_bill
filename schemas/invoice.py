from pydantic import BaseModel
from datetime import date

class InvoiceBase(BaseModel):
    customer_id: int
    date_from: date
    date_to: date
    due_date: date
    iban: str
    reference: str
    amount_net: float
    amount_gross: float

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    id: int
    class Config:
        orm_mode = True
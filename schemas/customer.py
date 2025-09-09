from pydantic import BaseModel, EmailStr, ConfigDict

class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    address: str
    post: str

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
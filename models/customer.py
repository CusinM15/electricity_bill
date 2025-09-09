from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy import Column, Integer, Unicode

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Unicode, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    address = Column(Unicode, unique=False, index=True, nullable=False)
    post = Column(Unicode, unique=False, index=True, nullable=False)
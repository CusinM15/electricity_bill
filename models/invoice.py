from sqlalchemy import Column, Integer, Float, Date, ForeignKey, String
from sqlalchemy.orm import relationship
from database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    iban = Column(String, nullable=False)
    reference = Column(String, nullable=False)
    amount_net = Column(Float, nullable=False)
    amount_gross = Column(Float, nullable=False)

    customer = relationship("Customer")
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP
from sqlalchemy.orm import relationship
from db import db
from enum import Enum as PyEnum
from config import Config

class PaymentMethodEnum(PyEnum):
    Online = 'Online'
    On_Spot = 'On_Spot'
    Credit_Card = 'Credit_Card'
    Debit_Card = 'Debit_Card'
    Gift_Card = 'Gift_Card'
    PayPal = 'PayPal'
    Cash = 'Cash'

class PaymentStatusEnum(PyEnum):
    Pending = 'Pending'
    Completed = 'Completed'
    Failed = 'Failed'
    Refunded = 'Refunded'

class CurrencyEnum(PyEnum):
    EUR = 'EUR'
    CZK = 'CZK'

class Payment(db.Model):
    __tablename__ = "payment"
    __table_args__ = {'schema': Config.POSTGRES_SCHEMA}
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Integer, nullable=False)
    payment_method = Column(Enum(PaymentMethodEnum), nullable=False)
    payment_status = Column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.Pending, nullable=False)
    transaction_id = Column(String(100))
    confirmation = Column(TIMESTAMP)
    currency = Column(Enum(CurrencyEnum), default=CurrencyEnum.EUR, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    rentals = relationship("Rental", back_populates="payment")
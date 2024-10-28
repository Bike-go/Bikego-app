from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP
from sqlalchemy.orm import relationship
from db import db

class Payment(db.Model):
    __tablename__ = "Payment"
    id = Column(Integer, primary_key=True)
    amount = Column(Integer, nullable=False)
    payment_method = Column(Enum('Online', 'On_Spot', 'Credit_Card', 'Debit_Card', 'Gift_Card', 'PayPal', 'Cash'), nullable=False)
    payment_status = Column(Enum('Pending', 'Completed', 'Failed', 'Refunded'), default='Pending', nullable=False)
    transaction_id = Column(String(100))
    confirmation = Column(TIMESTAMP)
    currency = Column(Enum('EUR', 'CZK'), default='EUR', nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    rentals = relationship("Rental", back_populates="payment")
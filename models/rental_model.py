from datetime import datetime
from sqlalchemy import TIMESTAMP, Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db

class Rental(db.Model):
    __tablename__ = "Rental"
    id = Column(Integer, primary_key=True)
    start_time = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    end_time = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    total_price = Column(Integer, nullable=False)
    User_id = Column(UUID, ForeignKey('User.id'), nullable=False)
    Payment_id = Column(Integer, ForeignKey('Payment.id'), nullable=False)
    Instance_Bike_id = Column(UUID, ForeignKey('Instance_Bike.id'), nullable=False)

    user = relationship("User", back_populates="rentals")
    payment = relationship("Payment", back_populates="rentals")
    instance_bike = relationship("InstanceBike", back_populates="rentals")
    inspections = relationship("Inspection", back_populates="rental")
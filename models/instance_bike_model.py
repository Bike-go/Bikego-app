from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Integer, Enum, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db

class InstanceBike(db.Model):
    __tablename__ = 'Instance_Bike'
    id = Column(UUID(as_uuid=True), primary_key=True)
    size = Column(Integer, nullable=False)
    color = Column(String(45), nullable=False)
    purchase_date = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    last_service_at = Column(TIMESTAMP, default=datetime.utcnow)
    status = Column(Enum('Available', 'Rented', 'Under_Repair', 'Out_of_Service'), nullable=False, default='Available')
    Bike_id = Column(UUID(as_uuid=True), ForeignKey('Bike.id', ondelete='CASCADE'), nullable=False)

    bike = relationship("Bike", back_populates="instances")
    reservations = relationship("Reservation", back_populates="instance_bike")
    rentals = relationship("Rental", back_populates="instance_bike")
    pictures = relationship("Picture", back_populates="instance_bike")
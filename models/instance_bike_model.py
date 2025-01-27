from datetime import datetime
import uuid
from sqlalchemy import Column, ForeignKey, String, Enum, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db
from enum import Enum as PyEnum
from config import Config

class BikeSizeEnum(PyEnum):
    XS = 'XS'
    S = 'S'
    M = 'M'
    L = 'L'
    XL = 'XL'
    XXL = 'XXL'

class BikeStatusEnum(PyEnum):
    Available = 'Available'
    Rented = 'Rented'
    Under_Repair = 'Under_Repair'
    Out_of_Service = 'Out_of_Service'

class InstanceBike(db.Model):
    __tablename__ = 'instance_Bike'
    __table_args__ = {'schema': Config.POSTGRES_SCHEMA}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    size = Column(Enum(BikeSizeEnum), nullable=False)
    color = Column(String(45), nullable=False)
    purchase_date = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    last_service_at = Column(TIMESTAMP, default=datetime.utcnow)
    status = Column(Enum(BikeStatusEnum), nullable=False, default=BikeStatusEnum.Available)
    Bike_id = Column(UUID(as_uuid=True), ForeignKey(f'{Config.POSTGRES_SCHEMA}.bike.id', ondelete='CASCADE'), nullable=False)

    bike = relationship("Bike", back_populates="instances")
    reservations = relationship("Reservation", back_populates="instance_bike")
    rentals = relationship("Rental", back_populates="instance_bike")
    pictures = relationship("Picture", back_populates="instance_bike")
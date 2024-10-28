from datetime import datetime
from sqlalchemy import Column, ForeignKey, String, Integer, Enum, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db

class Bike(db.Model):
    __tablename__ = "Bike"
    id = Column(UUID, primary_key=True)
    model = Column(String(45), nullable=False)
    size = Column(Integer, nullable=False)
    frame_material = Column(Enum('Aluminum', 'Carbon', 'Steel', 'Titanium'), nullable=False)
    brake_type = Column(Enum('Disc', 'Rim', 'Hydraulic'), nullable=False)
    brand = Column(String(45), nullable=False)
    color = Column(String(45), nullable=False)
    purchase_date = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    last_service_at = Column(TIMESTAMP, default=datetime.utcnow)
    description = Column(Text)
    Category_id = Column(Integer, ForeignKey('Category.id'), nullable=False)
    Price_id = Column(Integer, ForeignKey('Price.id'), nullable=False)

    category = relationship("Category", back_populates="bikes")
    price = relationship("Price", back_populates="bikes")
    reservations = relationship("Reservation", back_populates="bike")
    repairs = relationship("Repair", back_populates="bike")
    maintenances = relationship("Maintenance", back_populates="bike")
    rentals = relationship("Rental", back_populates="bike")
    pictures = relationship("Picture", back_populates="bike")
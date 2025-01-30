from sqlalchemy import Column, ForeignKey, String, Integer, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db

class Bike(db.Model):
    __tablename__ = "Bike"
    id = Column(UUID(as_uuid=True), primary_key=True)
    model = Column(String(45), nullable=False)
    frame_material = Column(Enum('Aluminum', 'Carbon', 'Steel', 'Titanium'), nullable=False)
    brake_type = Column(Enum('Disc', 'Rim', 'Hydraulic'), nullable=False)
    brand = Column(String(45), nullable=False)
    description = Column(Text)
    Category_id = Column(Integer, ForeignKey('Category.id'), nullable=False)
    Price_id = Column(Integer, ForeignKey('Price.id'), nullable=False)

    instances = relationship("InstanceBike", back_populates="bike")
    category = relationship("Category", back_populates="bikes")
    price = relationship("Price", back_populates="bikes")
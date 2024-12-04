import uuid
from sqlalchemy import Column, ForeignKey, String, Integer, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db
from enum import Enum as PyEnum
from config import Config

class FrameMaterialEnum(PyEnum):
    Aluminum = 'Aluminum'
    Carbon = 'Carbon'
    Steel = 'Steel'
    Titanium = 'Titanium'

class BrakeTypeEnum(PyEnum):
    Disc = 'Disc'
    Rim = 'Rim'
    Hydraulic = 'Hydraulic'

class Bike(db.Model):
    __tablename__ = "bike"
    __table_args__ = {'schema': Config.POSTGRES_SCHEMA}
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model = Column(String(45), nullable=False)
    frame_material = Column(Enum(FrameMaterialEnum), nullable=False)
    brake_type = Column(Enum(BrakeTypeEnum), nullable=False)
    brand = Column(String(45), nullable=False)
    description = Column(Text)
    Category_id = Column(Integer, ForeignKey(f'{Config.POSTGRES_SCHEMA}.category.id'), nullable=False)
    Price_id = Column(Integer, ForeignKey(f'{Config.POSTGRES_SCHEMA}.price.id'), nullable=False)

    instances = relationship("InstanceBike", back_populates="bike")
    category = relationship("Category", back_populates="bikes")
    price = relationship("Price", back_populates="bikes")
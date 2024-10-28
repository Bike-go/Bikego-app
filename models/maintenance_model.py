from datetime import datetime
from sqlalchemy import TIMESTAMP, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from db import db

class Maintenance(db.Model):
    __tablename__ = "Maintenance"
    id = Column(Integer, primary_key=True)
    description = Column(String(255))
    maintenance_date = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    User_id = Column(UUID, ForeignKey('User.id'), nullable=False)
    Bike_id = Column(UUID, ForeignKey('Bike.id'), nullable=False)

    user = relationship("User", back_populates="maintenances")
    bike = relationship("Bike", back_populates="maintenances")
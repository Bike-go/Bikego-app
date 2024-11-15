from datetime import datetime
from sqlalchemy import TIMESTAMP, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db

class Inspection(db.Model):
    __tablename__ = "Inspection"
    id = Column(Integer, primary_key=True)
    inspection_date = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    comments = Column(String(45))
    User_id = Column(UUID, ForeignKey('User.id'), nullable=False)
    Rental_id = Column(Integer, ForeignKey('Rental.id'), nullable=False)

    user = relationship("User", back_populates="inspections")
    rental = relationship("Rental", back_populates="inspections")
    repairs = relationship("Repair", back_populates="inspection")
    maintenances = relationship("Maintenance", back_populates="inspection")
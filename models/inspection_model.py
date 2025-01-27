from datetime import datetime
from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db
from config import Config

class Inspection(db.Model):
    __tablename__ = "inspection"
    __table_args__ = {'schema': Config.POSTGRES_SCHEMA}
    id = Column(Integer, primary_key=True, autoincrement=True)
    inspection_date = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    comments = Column(String(45))
    finished = Column(Boolean, default=False, nullable=False)
    User_id = Column(UUID, ForeignKey(f'{Config.POSTGRES_SCHEMA}.user.id'), nullable=False)
    Rental_id = Column(Integer, ForeignKey(f'{Config.POSTGRES_SCHEMA}.rental.id'), nullable=False)

    user = relationship("User", back_populates="inspections")
    rental = relationship("Rental", back_populates="inspections")
    repairs = relationship("Repair", back_populates="inspection")
    maintenances = relationship("Maintenance", back_populates="inspection")
from datetime import datetime
import os
from sqlalchemy import TIMESTAMP, Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db

class Inspection(db.Model):
    __tablename__ = "inspection"
    __table_args__ = {'schema': os.getenv('POSTGRES_SCHEMA', 'public')}
    id = Column(Integer, primary_key=True, autoincrement=True)
    inspection_date = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    inspectioncol = Column(String(45), nullable=False)
    brakes_status = Column(String(45), nullable=False)
    tires_status = Column(String(45), nullable=False)
    frame_status = Column(String(45), nullable=False)
    overall_condition = Column(String(45), nullable=False)
    comments = Column(String(45))
    User_id = Column(UUID, ForeignKey(f'{os.getenv("POSTGRES_SCHEMA", "public")}.user.id'), nullable=False)
    Rental_id = Column(Integer, ForeignKey(f'{os.getenv("POSTGRES_SCHEMA", "public")}.rental.id'), nullable=False)

    user = relationship("User", back_populates="inspections")
    rental = relationship("Rental", back_populates="inspections")
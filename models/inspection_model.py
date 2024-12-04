from datetime import datetime
from sqlalchemy import TIMESTAMP, Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db
from config import Config

class Inspection(db.Model):
    __tablename__ = "inspection"
    __table_args__ = {'schema': Config.POSTGRES_SCHEMA}
    id = Column(Integer, primary_key=True, autoincrement=True)
    inspection_date = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    inspectioncol = Column(String(45), nullable=False)
    brakes_status = Column(String(45), nullable=False)
    tires_status = Column(String(45), nullable=False)
    frame_status = Column(String(45), nullable=False)
    overall_condition = Column(String(45), nullable=False)
    comments = Column(String(45))
    User_id = Column(UUID, ForeignKey(f'{Config.POSTGRES_SCHEMA}.user.id'), nullable=False)
    Rental_id = Column(Integer, ForeignKey(f'{Config.POSTGRES_SCHEMA}.rental.id'), nullable=False)

    user = relationship("User", back_populates="inspections")
    rental = relationship("Rental", back_populates="inspections")
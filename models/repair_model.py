from datetime import datetime
from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db

class Repair(db.Model):
    __tablename__ = "Repair"
    id = Column(Integer, primary_key=True)
    description = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    User_id = Column(UUID, ForeignKey('User.id'), nullable=False)
    Bike_id = Column(UUID, ForeignKey('Bike.id'), nullable=False)

    user = relationship("User", back_populates="repairs")
    bike = relationship("Bike", back_populates="repairs")
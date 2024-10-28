from datetime import datetime
from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db

class Picture(db.Model):
    __tablename__ = "Picture"
    id = Column(Integer, primary_key=True)
    bike_picture_url = Column(String(255), nullable=False)
    picture_delete_hash = Column(String(255), nullable=False)
    description = Column(String(45))
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    Bike_id = Column(UUID, ForeignKey('Bike.id'), nullable=False)

    bike = relationship("Bike", back_populates="pictures")

from datetime import datetime
import os
from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db

class Picture(db.Model):
    __tablename__ = "picture"
    __table_args__ = {'schema': os.getenv('POSTGRES_SCHEMA', 'public')}
    id = Column(Integer, primary_key=True, autoincrement=True)
    bike_picture_url = Column(String(255), nullable=False)
    picture_delete_hash = Column(String(255), nullable=False)
    description = Column(String(45))
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    Instance_Bike_id = Column(UUID, ForeignKey(f'{os.getenv("POSTGRES_SCHEMA", "public")}.instance_Bike.id'), nullable=False)

    instance_bike = relationship("InstanceBike", back_populates="pictures")

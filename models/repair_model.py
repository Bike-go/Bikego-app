from datetime import datetime
import os
from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db

class Repair(db.Model):
    __tablename__ = "repair"
    __table_args__ = {'schema': os.getenv('POSTGRES_SCHEMA', 'public')}
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    User_id = Column(UUID, ForeignKey(f'{os.getenv("POSTGRES_SCHEMA", "public")}.user.id'), nullable=False)
    Instance_Bike_id = Column(UUID, ForeignKey(f'{os.getenv("POSTGRES_SCHEMA", "public")}.instance_Bike.id'), nullable=False)

    user = relationship("User", back_populates="repairs")
    instance_bike = relationship("InstanceBike", back_populates="repairs")
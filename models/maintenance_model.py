from datetime import datetime
import os
from sqlalchemy import TIMESTAMP, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from db import db

class Maintenance(db.Model):
    __tablename__ = "maintenance"
    __table_args__ = {'schema': os.getenv('POSTGRES_SCHEMA', 'public')}
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(255))
    maintenance_date = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    User_id = Column(UUID, ForeignKey(f'{os.getenv("POSTGRES_SCHEMA", "public")}.user.id'), nullable=False)
    Instance_Bike_id = Column(UUID, ForeignKey(f'{os.getenv("POSTGRES_SCHEMA", "public")}.instance_Bike.id'), nullable=False)

    user = relationship("User", back_populates="maintenances")
    instance_bike = relationship("InstanceBike", back_populates="maintenances")
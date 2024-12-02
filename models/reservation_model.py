from datetime import datetime
import os
from sqlalchemy import UUID, Column, Boolean, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from db import db

class Reservation(db.Model):
    __tablename__ = "reservation"
    __table_args__ = {'schema': os.getenv('POSTGRES_SCHEMA', 'public')}
    id = Column(Integer, primary_key=True, autoincrement=True)
    reservation_start = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    reservation_end = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    ready_to_pickup = Column(Boolean, nullable=False)
    User_id = Column(UUID(as_uuid=True), ForeignKey(f'{os.getenv("POSTGRES_SCHEMA", "public")}.user.id'), nullable=False)
    Instance_Bike_id = Column(UUID(as_uuid=True), ForeignKey(f'{os.getenv("POSTGRES_SCHEMA", "public")}.instance_Bike.id'), nullable=False)

    user = relationship("User", back_populates="reservations")
    instance_bike = relationship("InstanceBike", back_populates="reservations")
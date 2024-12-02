from datetime import datetime
import os
from sqlalchemy import TIMESTAMP, Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db

class Rental(db.Model):
    __tablename__ = "rental"
    __table_args__ = {'schema': os.getenv('POSTGRES_SCHEMA', 'public')}
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    end_time = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    total_price = Column(Integer, nullable=False)
    User_id = Column(UUID, ForeignKey(f'{os.getenv("POSTGRES_SCHEMA", "public")}.user.id'), nullable=False)
    Payment_id = Column(Integer, ForeignKey(f'{os.getenv("POSTGRES_SCHEMA", "public")}.payment.id'), nullable=False)
    Instance_Bike_id = Column(UUID, ForeignKey(f'{os.getenv("POSTGRES_SCHEMA", "public")}.instance_Bike.id'), nullable=False)

    user = relationship("User", back_populates="rentals")
    payment = relationship("Payment", back_populates="rentals")
    instance_bike = relationship("InstanceBike", back_populates="rentals")
    inspections = relationship("Inspection", back_populates="rental")
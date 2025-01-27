from datetime import datetime
from sqlalchemy import TIMESTAMP, Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db
from config import Config

class Rental(db.Model):
    __tablename__ = "rental"
    __table_args__ = {'schema': Config.POSTGRES_SCHEMA}
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    end_time = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    total_price = Column(Integer, nullable=False)
    User_id = Column(UUID, ForeignKey(f'{Config.POSTGRES_SCHEMA}.user.id'), nullable=False)
    Payment_id = Column(Integer, ForeignKey(f'{Config.POSTGRES_SCHEMA}.payment.id'))
    Instance_Bike_id = Column(UUID, ForeignKey(f'{Config.POSTGRES_SCHEMA}.instance_Bike.id'), nullable=False)

    user = relationship("User", back_populates="rentals")
    payment = relationship("Payment", back_populates="rentals")
    instance_bike = relationship("InstanceBike", back_populates="rentals")
    inspections = relationship("Inspection", back_populates="rental")
from datetime import datetime
from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db
from config import Config

class Repair(db.Model):
    __tablename__ = "repair"
    __table_args__ = {'schema': Config.POSTGRES_SCHEMA}
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    User_id = Column(UUID, ForeignKey(f'{Config.POSTGRES_SCHEMA}.user.id'), nullable=False)
    Instance_Bike_id = Column(UUID, ForeignKey(f'{Config.POSTGRES_SCHEMA}.instance_Bike.id'), nullable=False)

    user = relationship("User", back_populates="repairs")
    inspection = relationship("Inspection", back_populates="repairs")
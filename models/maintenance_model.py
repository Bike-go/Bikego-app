from datetime import datetime
from sqlalchemy import TIMESTAMP, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from db import db
from config import Config

class Maintenance(db.Model):
    __tablename__ = "maintenance"
    __table_args__ = {'schema': Config.POSTGRES_SCHEMA}
    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(255))
    maintenance_date = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    User_id = Column(UUID, ForeignKey(f'{Config.POSTGRES_SCHEMA}.user.id'), nullable=False)
    Inspection_id = Column(UUID, ForeignKey(f'{Config.POSTGRES_SCHEMA}.inspection.id'), nullable=False)

    user = relationship("User", back_populates="maintenances")
    inspection = relationship("Inspection", back_populates="maintenances")
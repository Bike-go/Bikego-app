from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from db import db
from config import Config

class Price(db.Model):
    __tablename__ = "price"
    __table_args__ = {'schema': Config.POSTGRES_SCHEMA}
    id = Column(Integer, primary_key=True, autoincrement=True)
    price_per_hour = Column(Integer, nullable=False)
    price_per_day = Column(Integer, nullable=False)

    bikes = relationship("Bike", back_populates="price")
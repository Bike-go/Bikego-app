import os
from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from db import db

class Price(db.Model):
    __tablename__ = "price"
    __table_args__ = {'schema': os.getenv('POSTGRES_SCHEMA', 'public')}
    id = Column(Integer, primary_key=True, autoincrement=True)
    price_per_hour = Column(Integer, nullable=False)
    price_per_day = Column(Integer, nullable=False)

    bikes = relationship("Bike", back_populates="price")
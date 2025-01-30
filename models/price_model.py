from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from db import db

class Price(db.Model):
    __tablename__ = "Price"
    id = Column(Integer, primary_key=True)
    price_per_hour = Column(Integer, nullable=False)
    price_per_day = Column(Integer, nullable=False)

    bikes = relationship("Bike", back_populates="price")
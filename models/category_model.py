from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from db import db

class Category(db.Model):
    __tablename__ = "Category"
    id = Column(Integer, primary_key=True)
    name = Column(String(45), unique=True, nullable=False)
    description = Column(Text)

    bikes = relationship("Bike", back_populates="category")
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from db import db
from config import Config

class Category(db.Model):
    __tablename__ = "category"
    __table_args__ = {'schema': Config.POSTGRES_SCHEMA}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), unique=True, nullable=False)
    description = Column(Text)

    bikes = relationship("Bike", back_populates="category")
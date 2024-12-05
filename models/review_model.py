from datetime import datetime
from config import Config
from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db

class Review(db.Model):
    __tablename__ = "review"
    __table_args__ = {'schema': Config.POSTGRES_SCHEMA}
    id = Column(Integer, primary_key=True, autoincrement=True)
    rating = Column(Integer, CheckConstraint('rating >= 1 AND rating <= 5'), nullable=False)
    comment = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    published_at = Column(TIMESTAMP)
    User_id = Column(UUID, ForeignKey(f'{Config.POSTGRES_SCHEMA}.user.id'), nullable=False)

    user = relationship("User", back_populates="reviews")
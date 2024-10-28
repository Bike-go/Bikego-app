from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db

class News(db.Model):
    __tablename__ = "News"
    id = Column(Integer, primary_key=True)
    title = Column(String(45), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    published_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    author_id = Column(UUID, ForeignKey('User.id'), nullable=True)

    author = relationship("User", back_populates="news")
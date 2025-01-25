from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db
from config import Config

class News(db.Model):
    __tablename__ = "news"
    __table_args__ = {'schema': Config.POSTGRES_SCHEMA}
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(45), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    published_at = Column(TIMESTAMP)
    author_id = Column(UUID, ForeignKey(f'{Config.POSTGRES_SCHEMA}.user.id'), nullable=True)

    author = relationship("User", back_populates="news")
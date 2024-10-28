from datetime import datetime
from sqlalchemy import Column, Enum, String, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db import db

class User(db.Model):
    __tablename__ = "User"
    id = Column(UUID, primary_key=True)
    username = Column(String(45), nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), nullable=False)
    phone_number = Column(String(15))
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    last_login = Column(TIMESTAMP)
    profile_picture_url = Column(String(255))
    picture_delete_hash = Column(String(255))
    email_verified = Column(Boolean, default=False, nullable=False)
    darkmode = Column(Boolean, default=False, nullable=False)
    role = Column(Enum('Admin', 'Employee', 'Customer'), nullable=False)

    news = relationship("News", back_populates="author")
    reservations = relationship("Reservation", back_populates="user")
    repairs = relationship("Repair", back_populates="user")
    maintenances = relationship("Maintenance", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    rentals = relationship("Rental", back_populates="user")
    inspections = relationship("Inspection", back_populates="user")
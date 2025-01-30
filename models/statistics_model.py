from sqlalchemy import Column, Integer, String, TIMESTAMP, Interval
from sqlalchemy.sql import func
from db import db

class Statistics(db.Model):
    __tablename__ = "Statistics"

    id = Column(Integer, primary_key=True)
    report_period = Column(TIMESTAMP, default=func.now())
    total_rentals = Column(Integer, default=0)
    total_income = Column(Integer, default=0)
    most_popular_bike = Column(String(45))
    average_rental_duration = Column(Interval)
    total_repairs = Column(Integer, default=0)
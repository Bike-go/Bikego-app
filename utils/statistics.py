from datetime import datetime, timedelta
from models import db
from models.statistics_model import Statistics
from models.rental_model import Rental
from models.bike_model import Bike
from models.maintenance_model import Maintenance

def generate_statistics():
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)  # Monthly statistics

    total_rentals = Rental.query.filter(Rental.start_time >= start_date).count()
    total_income = db.session.query(db.func.sum(Rental.total_price)).scalar()
    most_popular_bike = (
        db.session.query(Bike.model)
        .join(Rental, Rental.Bike_id == Bike.id)
        .filter(Rental.start_time >= start_date)
        .group_by(Bike.model)
        .order_by(db.func.count(Bike.id).desc())
        .first()
    )[0]
    average_rental_duration = (
        db.session.query(db.func.avg(Rental.end_time - Rental.start_time)).scalar()
    )
    total_repairs = Maintenance.query.filter(Maintenance.maintenance_date >= start_date).count()

    new_statistics = Statistics(
        report_period=end_date,
        total_rentals=total_rentals,
        total_income=total_income or 0,
        most_popular_bike=most_popular_bike,
        average_rental_duration=average_rental_duration,
        total_repairs=total_repairs,
    )

    db.session.add(new_statistics)
    db.session.commit()
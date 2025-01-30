from marshmallow import fields, EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.statistics_model import Statistics

class StatisticsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Statistics
        load_instance = True
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    report_period = fields.DateTime(required=False)
    total_rentals = fields.Int(required=False)
    total_income = fields.Int(required=False)
    most_popular_bike = fields.Str(required=False)
    average_rental_duration = fields.Time(required=False)
    total_repairs = fields.Int(required=False)
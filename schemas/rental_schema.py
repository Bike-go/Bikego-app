from marshmallow import fields, EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.rental_model import Rental

class RentalSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Rental
        load_instance = True
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    start_time = fields.DateTime(dump_only=True)
    end_time = fields.DateTime(dump_only=True)
    total_price = fields.Int(required=True)
    User_id = fields.UUID(required=True)
    Payment_id = fields.Int(required=True)
    Instance_Bike_id = fields.UUID(required=True)
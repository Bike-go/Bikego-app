from marshmallow import fields, EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.reservation_model import Reservation

class ReservationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Reservation
        load_instance = True
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    reservation_start = fields.DateTime(dump_only=True)
    reservation_end = fields.DateTime(dump_only=True)
    ready_to_pickup = fields.Bool(required=True)
    User_id = fields.UUID(required=True)
    Instance_Bike_id = fields.UUID(required=True)
from marshmallow import fields, EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.price_model import Price

class PriceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Price
        load_instance = True
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    price_per_hour = fields.Int(required=True)
    price_per_day = fields.Int(required=True)
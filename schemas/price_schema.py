from marshmallow import Schema, fields, EXCLUDE
from models.price_model import Price

class PriceSchema(Schema):
    class Meta:
        model = Price
        load_instance = True
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    price_per_hour = fields.Int(required=True)
    price_per_day = fields.Int(required=True)
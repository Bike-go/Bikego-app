from marshmallow import Schema, fields, validate, EXCLUDE
from models.bike_model import Bike

class BikeSchema(Schema):
    class Meta:
        model = Bike
        load_instance = True
        unknown = EXCLUDE

    id = fields.UUID(dump_only=True)
    model = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    frame_material = fields.Str(required=True, validate=validate.OneOf(['Aluminum', 'Carbon', 'Steel', 'Titanium']))
    brake_type = fields.Str(required=True, validate=validate.OneOf(['Disc', 'Rim', 'Hydraulic']))
    brand = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    description = fields.Str(required=False)
    Category_id = fields.Int(required=True)
    Price_id = fields.Int(required=True)
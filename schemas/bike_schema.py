from marshmallow import fields, validate, EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.bike_model import Bike

class BikeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Bike
        load_instance = True
        unknown = EXCLUDE

    id = fields.UUID(dump_only=True)
    model = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    size = fields.Int(required=True, validate=validate.Range(min=1))
    frame_material = fields.Str(required=True, validate=validate.OneOf(['Aluminum', 'Carbon', 'Steel', 'Titanium']))
    brake_type = fields.Str(required=True, validate=validate.OneOf(['Disc', 'Rim', 'Hydraulic']))
    brand = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    color = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    purchase_date = fields.DateTime(dump_only=True)
    last_service_at = fields.DateTime(required=False)
    description = fields.Str(required=False)
    Category_id = fields.Int(required=True)
    Price_id = fields.Int(required=True)
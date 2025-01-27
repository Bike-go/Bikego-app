from marshmallow import Schema, fields, validate, EXCLUDE
from models.instance_bike_model import InstanceBike

class InstanceBikeSchema(Schema):
    class Meta:
        model = InstanceBike
        load_instance = True
        unknown = EXCLUDE

    id = fields.UUID(dump_only=True)
    size = fields.Int(required=True, validate=validate.Range(min=1))
    color = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    purchase_date = fields.DateTime(dump_only=True)
    last_service_at = fields.DateTime(required=False)
    status = fields.Str(required=True, validate=validate.OneOf(['Available', 'Rented', 'Under Maintenance', 'Under Repair']))
    Bike_id = fields.UUID(required=True)
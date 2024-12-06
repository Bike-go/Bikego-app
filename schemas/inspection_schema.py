from marshmallow import Schema, fields, validate, EXCLUDE
from models.inspection_model import Inspection

class InspectionSchema(Schema):
    class Meta:
        model = Inspection
        load_instance = True
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    inspection_date = fields.DateTime(dump_only=True)
    comments = fields.Str(required=False, validate=validate.Length(max=45))
    User_id = fields.UUID(required=True)
    Rental_id = fields.Int(required=True)
from marshmallow import fields, validate, EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.inspection_model import Inspection

class InspectionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Inspection
        load_instance = True
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    inspection_date = fields.DateTime(dump_only=True)
    inspectioncol = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    brakes_status = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    tires_status = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    frame_status = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    overall_condition = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    comments = fields.Str(required=False, validate=validate.Length(max=45))
    User_id = fields.UUID(required=True)
    Rental_id = fields.Int(required=True)
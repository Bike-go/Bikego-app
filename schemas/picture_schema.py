from marshmallow import fields, validate, EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.picture_model import Picture

class PictureSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Picture
        load_instance = True
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    bike_picture_url = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    picture_delete_hash = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(required=False, validate=validate.Length(max=45))
    created_at = fields.DateTime(dump_only=True)
    Instance_Bike_id = fields.UUID(required=True)
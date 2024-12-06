from marshmallow import Schema, fields, validate, EXCLUDE
from models.category_model import Category

class CategorySchema(Schema):
    class Meta:
        model = Category
        load_instance = True
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    description = fields.Str(required=False)
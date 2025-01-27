from marshmallow import Schema, fields, validate, EXCLUDE
from models.review_model import Review

class ReviewSchema(Schema):
    class Meta:
        model = Review
        load_instance = True
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    rating = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    comment = fields.Str(required=False)
    created_at = fields.DateTime(dump_only=True)
    published_at = fields.DateTime(required=False)
    User_id = fields.UUID(required=True)
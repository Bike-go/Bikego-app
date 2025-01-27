from marshmallow import Schema, fields, validate, EXCLUDE
from models.news_model import News

class NewsSchema(Schema):
    class Meta:
        model = News
        load_instance = True
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    content = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    published_at = fields.DateTime(required=True)
    author_id = fields.UUID(required=False)
from marshmallow import fields, EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.repair_model import Repair

class RepairSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Repair
        load_instance = True
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    description = fields.Str(required=False)
    created_at = fields.DateTime(dump_only=True)
    User_id = fields.UUID(required=True)
    Inspection_id = fields.UUID(required=True)
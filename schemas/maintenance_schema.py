from marshmallow import fields, EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.maintenance_model import Maintenance

class MaintenanceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Maintenance
        load_instance = True
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    description = fields.Str(required=False)
    maintenance_date = fields.DateTime(dump_only=True)
    User_id = fields.UUID(required=True)
    Inspection_id = fields.UUID(required=True)
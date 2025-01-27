from marshmallow import Schema, fields, validate, EXCLUDE
from models.payment_model import Payment

class PaymentSchema(Schema):
    class Meta:
        model = Payment
        load_instance = True
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    amount = fields.Int(required=True)
    payment_method = fields.Str(required=True, validate=validate.OneOf(['Online', 'On_Spot', 'Credit_Card', 'Debit_Card', 'Gift_Card', 'PayPal', 'Cash']))
    payment_status = fields.Str(required=True, validate=validate.OneOf(['Pending', 'Completed', 'Failed', 'Refunded']))
    transaction_id = fields.Str(required=False)
    confirmation = fields.DateTime(required=False)
    currency = fields.Str(required=True, validate=validate.OneOf(['EUR', 'CZK']))
    created_at = fields.DateTime(dump_only=True)
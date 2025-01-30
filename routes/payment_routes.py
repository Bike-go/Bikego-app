from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.payment_model import Payment
from schemas.payment_schema import PaymentSchema
from utils.validator_utils import is_admin_or_employee
from db import db

payment_bp = Blueprint('payment_bp', __name__)

# Create a new payment
@payment_bp.route("/payments", methods=["POST"])
@jwt_required()
def create_payment():
    json_data = request.get_json()

    # Validate the request data
    if not json_data:
        return jsonify({"msg": "No input data provided"}), 400

    try:
        payment_data = PaymentSchema().load(json_data)
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

    payment = Payment(**payment_data)
    db.session.add(payment)
    db.session.commit()

    return PaymentSchema().jsonify(payment), 201

# Get a payment by ID
@payment_bp.route("/payments/<int:payment_id>", methods=["GET"])
@jwt_required()
def get_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    return PaymentSchema().jsonify(payment), 200

# Update an existing payment
@payment_bp.route("/payments/<int:payment_id>", methods=["PUT"])
@jwt_required()
def update_payment(payment_id):
    json_data = request.get_json()
    payment = Payment.query.get_or_404(payment_id)

    # Update payment fields
    payment.amount = json_data.get("amount", payment.amount)
    payment.payment_method = json_data.get("payment_method", payment.payment_method)
    payment.payment_status = json_data.get("payment_status", payment.payment_status)
    payment.transaction_id = json_data.get("transaction_id", payment.transaction_id)
    payment.confirmation = json_data.get("confirmation", payment.confirmation)
    payment.currency = json_data.get("currency", payment.currency)

    db.session.commit()

    return PaymentSchema().jsonify(payment), 200

# Delete a payment
@payment_bp.route("/payments/<int:payment_id>", methods=["DELETE"])
@jwt_required()
def delete_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    db.session.delete(payment)
    db.session.commit()

    return jsonify({"msg": "Payment deleted."}), 204

# Get all payments with pagination
@payment_bp.route("/payments", methods=["GET"])
@jwt_required()
def get_all_payments():
    if not is_admin_or_employee():
        return jsonify({"msg": "Access denied."}), 403

    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)

    payments = Payment.query.limit(limit).offset(offset).all()
    return PaymentSchema(many=True).jsonify(payments), 200
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.rental_model import Rental
from schemas.rental_schema import RentalSchema
from db import db

rental_bp = Blueprint('rental', __name__)

# Create a new rental
@rental_bp.route("/rentals", methods=["POST"])
@jwt_required()
def create_rental():
    current_user = get_jwt_identity()
    json_data = request.get_json()

    # Validate the request data
    if not json_data:
        return jsonify({"msg": "No input data provided"}), 400

    try:
        rental_data = RentalSchema().load(json_data)
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

    rental = Rental(**rental_data)
    db.session.add(rental)
    db.session.commit()

    return RentalSchema().jsonify(rental), 201

# Get a rental by ID
@rental_bp.route("/rentals/<int:rental_id>", methods=["GET"])
@jwt_required()
def get_rental(rental_id):
    rental = Rental.query.get_or_404(rental_id)
    return RentalSchema().jsonify(rental), 200

# Update an existing rental
@rental_bp.route("/rentals/<int:rental_id>", methods=["PUT"])
@jwt_required()
def update_rental(rental_id):
    current_user = get_jwt_identity()
    json_data = request.get_json()
    rental = Rental.query.get_or_404(rental_id)

    # Update rental fields
    rental.start_time = json_data.get("start_time", rental.start_time)
    rental.end_time = json_data.get("end_time", rental.end_time)
    rental.total_price = json_data.get("total_price", rental.total_price)
    rental.user_id = json_data.get("user_id", rental.user_id)
    rental.payment_id = json_data.get("payment_id", rental.payment_id)
    rental.bike_id = json_data.get("bike_id", rental.bike_id)

    db.session.commit()

    return RentalSchema().jsonify(rental), 200

# Delete a rental
@rental_bp.route("/rentals/<int:rental_id>", methods=["DELETE"])
@jwt_required()
def delete_rental(rental_id):
    rental = Rental.query.get_or_404(rental_id)
    db.session.delete(rental)
    db.session.commit()

    return jsonify({"msg": "Rental deleted."}), 204

# Get all rentals
@rental_bp.route("/rentals", methods=["GET"])
@jwt_required()
def get_all_rentals():
    # Get pagination parameters from the request
    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)

    # Query rentals with pagination
    rentals = Rental.query.limit(limit).offset(offset).all()

    return RentalSchema(many=True).jsonify(rentals), 200
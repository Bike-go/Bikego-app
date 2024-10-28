from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.price_model import Price
from schemas.price_schema import PriceSchema
from db import db

price_bp = Blueprint('price_bp', __name__)

# Create a new price
@price_bp.route("/prices", methods=["POST"])
@jwt_required()
def create_price():
    json_data = request.get_json()

    # Validate the request data
    if not json_data:
        return jsonify({"msg": "No input data provided"}), 400

    try:
        price_data = PriceSchema().load(json_data)
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

    price = Price(**price_data)
    db.session.add(price)
    db.session.commit()

    return PriceSchema().jsonify(price), 201

# Get a price by ID
@price_bp.route("/prices/<int:price_id>", methods=["GET"])
@jwt_required()
def get_price(price_id):
    price = Price.query.get_or_404(price_id)
    return PriceSchema().jsonify(price), 200

# Update an existing price
@price_bp.route("/prices/<int:price_id>", methods=["PUT"])
@jwt_required()
def update_price(price_id):
    json_data = request.get_json()
    price = Price.query.get_or_404(price_id)

    # Update price fields
    price.price_per_hour = json_data.get("price_per_hour", price.price_per_hour)
    price.price_per_day = json_data.get("price_per_day", price.price_per_day)

    db.session.commit()

    return PriceSchema().jsonify(price), 200

# Delete a price
@price_bp.route("/prices/<int:price_id>", methods=["DELETE"])
@jwt_required()
def delete_price(price_id):
    price = Price.query.get_or_404(price_id)
    db.session.delete(price)
    db.session.commit()

    return jsonify({"msg": "Price deleted."}), 204

# Get all prices with pagination
@price_bp.route("/prices", methods=["GET"])
def get_all_prices():
    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)
    
    prices = Price.query.limit(limit).offset(offset).all()
    return PriceSchema(many=True).jsonify(prices), 200
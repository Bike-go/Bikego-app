from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.bike_model import Bike
from schemas.bike_schema import BikeSchema
from db import db

bike_bp = Blueprint('bike_bp', __name__)

# Create a new bike
@bike_bp.route("/bikes", methods=["POST"])
@jwt_required()
def create_bike():
    json_data = request.get_json()

    # Validate the request data
    if not json_data:
        return jsonify({"msg": "No input data provided"}), 400

    try:
        bike_data = BikeSchema().load(json_data)
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

    bike = Bike(**bike_data)
    db.session.add(bike)
    db.session.commit()

    return BikeSchema().jsonify(bike), 201

# Get a bike by ID
@bike_bp.route("/bikes/<uuid:bike_id>", methods=["GET"])
@jwt_required()
def get_bike(bike_id):
    bike = Bike.query.get_or_404(bike_id)
    return BikeSchema().jsonify(bike), 200

# Update an existing bike
@bike_bp.route("/bikes/<uuid:bike_id>", methods=["PUT"])
@jwt_required()
def update_bike(bike_id):
    json_data = request.get_json()
    bike = Bike.query.get_or_404(bike_id)

    # Update bike fields
    bike.model = json_data.get("model", bike.model)
    bike.size = json_data.get("size", bike.size)
    bike.frame_material = json_data.get("frame_material", bike.frame_material)
    bike.brake_type = json_data.get("brake_type", bike.brake_type)
    bike.brand = json_data.get("brand", bike.brand)
    bike.color = json_data.get("color", bike.color)
    bike.last_service_at = json_data.get("last_service_at", bike.last_service_at)
    bike.description = json_data.get("description", bike.description)
    bike.Category_id = json_data.get("Category_id", bike.Category_id)
    bike.Price_id = json_data.get("Price_id", bike.Price_id)

    db.session.commit()

    return BikeSchema().jsonify(bike), 200

# Delete a bike
@bike_bp.route("/bikes/<uuid:bike_id>", methods=["DELETE"])
@jwt_required()
def delete_bike(bike_id):
    bike = Bike.query.get_or_404(bike_id)
    db.session.delete(bike)
    db.session.commit()

    return jsonify({"msg": "Bike deleted."}), 204

# Get all bikes
@bike_bp.route("/bikes", methods=["GET"])
def get_all_bikes():
    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)
    
    # Query the bikes with limit and offset
    bikes = Bike.query.limit(limit).offset(offset).all()
    
    return BikeSchema(many=True).jsonify(bikes), 200
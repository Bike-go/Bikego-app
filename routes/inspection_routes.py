from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.inspection_model import Inspection
from schemas.inspection_schema import InspectionSchema
from utils.validator_utils import is_admin_or_employee
from db import db

inspection_bp = Blueprint('inspection_bp', __name__)

# Create a new inspection
@inspection_bp.route("/inspections", methods=["POST"])
@jwt_required()
def create_inspection():
    if not is_admin_or_employee():  # Check user role
        return jsonify({"msg": "Access denied."}), 403

    json_data = request.get_json()
    try:
        inspection_data = InspectionSchema().load(json_data)
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

    inspection = Inspection(**inspection_data)
    db.session.add(inspection)
    db.session.commit()

    return InspectionSchema().jsonify(inspection), 201

# Get an inspection by ID
@inspection_bp.route("/inspections/<int:inspection_id>", methods=["GET"])
@jwt_required()
def get_inspection(inspection_id):
    if not is_admin_or_employee():  # Check user role
        return jsonify({"msg": "Access denied."}), 403

    inspection = Inspection.query.get_or_404(inspection_id)
    return InspectionSchema().jsonify(inspection), 200

# Update an existing inspection
@inspection_bp.route("/inspections/<int:inspection_id>", methods=["PUT"])
@jwt_required()
def update_inspection(inspection_id):
    if not is_admin_or_employee():  # Check user role
        return jsonify({"msg": "Access denied."}), 403

    json_data = request.get_json()
    inspection = Inspection.query.get_or_404(inspection_id)

    inspection.comments = json_data.get("comments", inspection.comments)

    db.session.commit()

    return InspectionSchema().jsonify(inspection), 200

# Delete an inspection
@inspection_bp.route("/inspections/<int:inspection_id>", methods=["DELETE"])
@jwt_required()
def delete_inspection(inspection_id):
    if not is_admin_or_employee():  # Check user role
        return jsonify({"msg": "Access denied."}), 403

    inspection = Inspection.query.get_or_404(inspection_id)
    db.session.delete(inspection)
    db.session.commit()

    return jsonify({"msg": "Inspection deleted."}), 204

# Get all inspections
@inspection_bp.route("/inspections", methods=["GET"])
@jwt_required()
def get_all_inspections():
    if not is_admin_or_employee():  # Check user role
        return jsonify({"msg": "Access denied."}), 403

    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)

    # Retrieve paginated inspections
    inspections = Inspection.query.limit(limit).offset(offset).all()
    return InspectionSchema(many=True).jsonify(inspections), 200

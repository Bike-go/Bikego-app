from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.maintenance_model import Maintenance
from schemas.maintenance_schema import MaintenanceSchema
from utils.validator_utils import is_admin_or_employee
from db import db

maintenance_bp = Blueprint('maintenance_bp', __name__)

@maintenance_bp.route("/maintenance", methods=["POST"])
@jwt_required()
def create_maintenance():
    if not is_admin_or_employee():
        return jsonify({"msg": "Access denied."}), 403

    json_data = request.get_json()
    maintenance_schema = MaintenanceSchema()
    try:
        maintenance_data = maintenance_schema.load(json_data)
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

    maintenance = Maintenance(**maintenance_data)
    db.session.add(maintenance)
    db.session.commit()

    return maintenance_schema.jsonify(maintenance), 201

@maintenance_bp.route("/maintenance/<int:maintenance_id>", methods=["GET"])
@jwt_required()
def get_maintenance(maintenance_id):
    if not is_admin_or_employee():
        return jsonify({"msg": "Access denied."}), 403

    maintenance = Maintenance.query.get_or_404(maintenance_id)
    return MaintenanceSchema().jsonify(maintenance), 200

@maintenance_bp.route("/maintenance/<int:maintenance_id>", methods=["PUT"])
@jwt_required()
def update_maintenance(maintenance_id):
    if not is_admin_or_employee():
        return jsonify({"msg": "Access denied."}), 403

    json_data = request.get_json()
    maintenance = Maintenance.query.get_or_404(maintenance_id)

    description = json_data.get('description', maintenance.description)

    maintenance.description = description

    db.session.commit()

    return MaintenanceSchema().jsonify(maintenance), 200

@maintenance_bp.route("/maintenance/<int:maintenance_id>", methods=["DELETE"])
@jwt_required()
def delete_maintenance(maintenance_id):
    if not is_admin_or_employee():
        return jsonify({"msg": "Access denied."}), 403

    maintenance = Maintenance.query.get_or_404(maintenance_id)
    db.session.delete(maintenance)
    db.session.commit()

    return jsonify({"msg": "Maintenance record deleted."}), 204

@maintenance_bp.route("/maintenance", methods=["GET"])
@jwt_required()
def get_all_maintenance():
    if not is_admin_or_employee():
        return jsonify({"msg": "Access denied."}), 403

    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)

    # Fetch maintenance records with pagination
    maintenance_records = Maintenance.query.limit(limit).offset(offset).all()
    
    return MaintenanceSchema(many=True).jsonify(maintenance_records), 200
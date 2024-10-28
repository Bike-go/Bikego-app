from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.repair_model import Repair
from schemas.repair_schema import RepairSchema
from utils.validator_utils import is_admin_or_employee
from db import db

repair_bp = Blueprint('repair_bp', __name__)

@repair_bp.route("/repairs", methods=["POST"])
@jwt_required()
def create_repair():
    # Check if user has the appropriate role
    user_id = get_jwt_identity()
    if not is_admin_or_employee(user_id):
        return {"msg": "Access denied. User must be an Admin or Employee."}, 403

    data = request.get_json()

    repair = Repair(
        description=data['description'],
        User_id=data['User_id'],
        Bike_id=data['Bike_id']
    )
    db.session.add(repair)
    db.session.commit()
    return RepairSchema().jsonify(repair), 201

@repair_bp.route("/repairs/<uuid:repair_id>", methods=["GET"])
@jwt_required()
def get_repair(repair_id):
    # Check if user has the appropriate role
    user_id = get_jwt_identity()
    if not is_admin_or_employee(user_id):
        return {"msg": "Access denied. User must be an Admin or Employee."}, 403

    repair = Repair.query.get_or_404(repair_id)
    return RepairSchema().jsonify(repair), 200

@repair_bp.route("/repairs/<uuid:repair_id>", methods=["PUT"])
@jwt_required()
def update_repair(repair_id):
    # Check if user has the appropriate role
    user_id = get_jwt_identity()
    if not is_admin_or_employee(user_id):
        return {"msg": "Access denied. User must be an Admin or Employee."}, 403

    repair = Repair.query.get_or_404(repair_id)
    data = request.get_json()

    if 'description' in data:
        repair.description = data['description']

    db.session.commit()
    return RepairSchema().jsonify(repair), 200

@repair_bp.route("/repairs/<uuid:repair_id>", methods=["DELETE"])
@jwt_required()
def delete_repair(repair_id):
    # Check if user has the appropriate role
    user_id = get_jwt_identity()
    if not is_admin_or_employee(user_id):
        return {"msg": "Access denied. User must be an Admin or Employee."}, 403

    repair = Repair.query.get_or_404(repair_id)
    db.session.delete(repair)
    db.session.commit()
    return {"message": "Repair deleted successfully."}, 204

@repair_bp.route("/repairs", methods=["GET"])
@jwt_required()
def get_repairs():
    # Check if user has the appropriate role
    user_id = get_jwt_identity()
    if not is_admin_or_employee(user_id):
        return {"msg": "Access denied. User must be an Admin or Employee."}, 403

    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)

    repairs = Repair.query \
        .order_by(Repair.created_at.desc()) \
        .limit(limit) \
        .offset(offset) \
        .all()
    
    return RepairSchema(many=True).jsonify(repairs), 200
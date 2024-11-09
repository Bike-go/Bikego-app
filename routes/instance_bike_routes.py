from datetime import datetime
from flask import Blueprint, request, jsonify
from models.instance_bike_model import InstanceBike
from schemas.instance_bike_schema import InstanceBikeSchema
from db import db
from uuid import uuid4

instance_bike_bp = Blueprint('instance_bike_bp', __name__)

@instance_bike_bp.route('/instance_bike', methods=['POST'])
def create_instance_bike():
    data = request.get_json()
    try:
        instance_bike_data = InstanceBikeSchema(**data)
        new_instance_bike = InstanceBike(
            id=uuid4(),
            size=instance_bike_data.size,
            color=instance_bike_data.color,
            purchase_date=instance_bike_data.purchase_date or datetime.utcnow(),
            last_service_at=instance_bike_data.last_service_at,
            status=instance_bike_data.status,
            Bike_id=instance_bike_data.Bike_id
        )
        db.add(new_instance_bike)
        db.commit()
        return jsonify(instance_bike_data.dict()), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

@instance_bike_bp.route('/instance_bike<uuid:id>', methods=['GET'])
def get_instance_bike(id):
    instance_bike = db.query(InstanceBike).filter_by(id=id).first()
    if instance_bike:
        return jsonify(InstanceBike.from_orm(instance_bike).dict()), 200
    return jsonify({"error": "Instance bike not found"}), 404

@instance_bike_bp.route('/instance_bike<uuid:id>', methods=['PUT'])
def update_instance_bike(id):
    data = request.get_json()
    instance_bike = db.query(InstanceBike).filter_by(id=id).first()
    if not instance_bike:
        return jsonify({"error": "Instance bike not found"}), 404
    try:
        updated_data = InstanceBikeSchema(**data)
        for field, value in updated_data.dict(exclude_unset=True).items():
            setattr(instance_bike, field, value)
        db.commit()
        return jsonify(InstanceBike.from_orm(instance_bike).dict()), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

@instance_bike_bp.route('/instance_bike<uuid:id>', methods=['DELETE'])
def delete_instance_bike(id):
    instance_bike = db.query(InstanceBike).filter_by(id=id).first()
    if not instance_bike:
        return jsonify({"error": "Instance bike not found"}), 404
    try:
        db.delete(instance_bike)
        db.commit()
        return jsonify({"message": "Instance bike deleted"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
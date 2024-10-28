from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from models.reservation_model import Reservation
from schemas.reservation_schema import ReservationSchema
from db import db

reservation_bp = Blueprint('reservations_bp', __name__)

@reservation_bp.route("/reservations", methods=["GET"])
@jwt_required()
def get_reservations():
    reservations = Reservation.query.all()
    return ReservationSchema(many=True).jsonify(reservations), 200

@reservation_bp.route("/reservations", methods=["POST"])
@jwt_required()
def create_reservation():
    data = request.get_json()
    reservation_schema = ReservationSchema()

    # Validate and deserialize input
    try:
        reservation = reservation_schema.load(data)
    except Exception as e:
        return {"message": str(e)}, 400

    new_reservation = Reservation(
        reservation_start=reservation['reservation_start'],
        reservation_end=reservation['reservation_end'],
        ready_to_pickup=reservation['ready_to_pickup'],
        User_id=reservation['User_id'],
        Bike_id=reservation['Bike_id']
    )
    
    db.session.add(new_reservation)
    db.session.commit()

    return reservation_schema.jsonify(new_reservation), 201

@reservation_bp.route("/reservations/<int:id>", methods=["GET"])
@jwt_required()
def get_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    return ReservationSchema().jsonify(reservation), 200

@reservation_bp.route("/reservations/<int:id>", methods=["PUT"])
@jwt_required()
def update_reservation(id):
    data = request.get_json()
    reservation = Reservation.query.get_or_404(id)
    reservation_schema = ReservationSchema()

    try:
        updated_reservation = reservation_schema.load(data, instance=reservation, partial=True)
        db.session.commit()
        return reservation_schema.jsonify(updated_reservation), 200
    except Exception as e:
        return {"message": str(e)}, 400

@reservation_bp.route("/reservations/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    db.session.delete(reservation)
    db.session.commit()
    return {"message": "Reservation deleted successfully."}, 200
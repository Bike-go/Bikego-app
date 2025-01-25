from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
import db
from models.inspection_model import Inspection
from models.instance_bike_model import BikeStatusEnum, InstanceBike
from models.rental_model import Rental
from models.user_model import User

servis_bp = Blueprint("servis_bp", __name__)


@servis_bp.route("/servis", methods=["GET", "POST"])
@jwt_required()
def servis():
    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user or user.role.value not in ["Admin", "Service"]:
        return redirect(url_for("home_bp.home"))

    csrf_token_from_jwt = get_jwt().get("csrf")

    if request.method == "POST":
        inspection_id = request.form.get("inspection_id")
        new_status = request.form.get("status")

        inspection = Inspection.query.get(inspection_id)
        if not inspection:
            flash("Inspection not found.", "error")
            return redirect(url_for("servis_bp.servis"))

        instance_bike = (
            InstanceBike.query.join(Rental, Rental.Instance_Bike_id == InstanceBike.id)
            .filter(Rental.id == inspection.Rental_id)
            .first()
        )

        if not instance_bike:
            flash("Associated bike not found.", "error")
            return redirect(url_for("servis_bp.servis"))

        valid_statuses = [status.value for status in BikeStatusEnum]
        if new_status not in valid_statuses:
            flash("Invalid status value.", "error")
            return redirect(url_for("servis_bp.servis"))

        try:
            instance_bike.status = new_status
            db.session.commit()
            flash("Bike status updated successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating bike status: {e}", "error")

        return redirect(url_for("servis_bp.servis"))

    inspections = (
        Inspection.query.join(Rental, Rental.id == Inspection.Rental_id)
        .join(InstanceBike, Rental.Instance_Bike_id == InstanceBike.id)
        .order_by(Inspection.inspection_date.desc())
        .all()
    )

    valid_statuses = [status.value for status in BikeStatusEnum]

    return (
        render_template(
            "servis.jinja",
            title="Servis",
            page="servis",
            inspections=inspections,
            statuses=valid_statuses,
            csrf_token=csrf_token_from_jwt,
        ),
        200,
    )

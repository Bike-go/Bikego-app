from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError
from models.inspection_model import Inspection
from models.instance_bike_model import BikeStatusEnum, InstanceBike
from models.rental_model import Rental
from utils.barcode import generate_barcode_svg
from utils.validator_utils import is_admin_or_service
from db import db

servis_bp = Blueprint("servis_bp", __name__)


@servis_bp.route("/servis", methods=["GET", "POST"])
@jwt_required()
def servis():
    get_jwt_identity()

    if is_admin_or_service():
        return redirect(url_for("home_bp.home")), 403

    csrf_token_from_jwt = get_jwt().get("csrf")
    valid_statuses = [status.value for status in BikeStatusEnum]

    if request.method == "POST":
        inspection_id = request.form.get("inspection_id")

        # Fetch the inspection
        inspection = Inspection.query.get(inspection_id)
        if not inspection:
            flash("Inspection not found.", "error")
            return redirect(url_for("servis_bp.servis")), 404

        # Update the finished field for the inspection
        try:
            inspection.finished = True
            db.session.commit()

            # After updating, check if all inspections for the rental_id are finished
            rental_id = inspection.Rental_id
            instance_bike = (
                InstanceBike.query.join(
                    Rental, Rental.Instance_Bike_id == InstanceBike.id
                )
                .filter(Rental.id == rental_id)
                .first()
            )

            if instance_bike:
                # Check if all inspections for the rental_id are finished
                all_finished = Inspection.query.filter_by(Rental_id=rental_id).all()
                if all(inspection.finished for inspection in all_finished):
                    # If all inspections are finished, update the bike status to 'available'
                    instance_bike.status = "Available"
                    db.session.commit()

            flash("Inspection status updated successfully.", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(
                f"An error occurred while updating the inspection status: {e}", "error"
            )

        return redirect(url_for("servis_bp.servis"))

    # Pagination parameters
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    # Fetch paginated inspections
    inspections = (
        Inspection.query.join(Rental, Rental.id == Inspection.Rental_id)
        .join(InstanceBike, Rental.Instance_Bike_id == InstanceBike.id)
        .filter(Inspection.finished == False)
        .order_by(Inspection.inspection_date.desc())
        .paginate(page=page, per_page=per_page)
    )

    inspections_with_barcode = []
    for inspection in inspections.items:
        barcode_svg = generate_barcode_svg(inspection.rental.instance_bike.id)

        # Ensure the barcode SVG is a string
        barcode_svg_str = (
            barcode_svg.decode("utf-8")
            if isinstance(barcode_svg, bytes)
            else barcode_svg
        )

        inspections_with_barcode.append(
            {"inspection": inspection, "barcode_svg": barcode_svg_str}
        )

    return render_template(
        "servis.jinja",
        title="Servis",
        page="servis",
        inspections=inspections_with_barcode,
        total_pages=inspections.pages,
        current_page=inspections.page,
        statuses=valid_statuses,
        csrf_token=csrf_token_from_jwt,
    )

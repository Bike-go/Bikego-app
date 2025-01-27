from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_jwt_extended import (
    get_jwt,
    jwt_required,
    get_jwt_identity,
    verify_jwt_in_request,
)
from db import db
from models.bike_model import Bike, BrakeTypeEnum, FrameMaterialEnum
from models.inspection_model import Inspection
from models.instance_bike_model import BikeSizeEnum, BikeStatusEnum, InstanceBike
from models.price_model import Price
from models.rental_model import Rental
from models.reservation_model import Reservation
from flask_wtf.csrf import generate_csrf
from models.user_model import User
from utils.barcode import generate_barcode_svg
from utils.validator_utils import is_admin_or_employee

rentals_bp = Blueprint("rentals_bp", __name__)


@rentals_bp.route("/rentals", methods=["GET"])
def rentals():
    brand_filter = request.args.getlist("brand")
    model_filter = request.args.getlist("model")
    frame_material_filter = request.args.getlist("frame_material")
    brake_type_filter = request.args.getlist("brake_type")
    size_filter = request.args.getlist("size")
    color_filter = request.args.getlist("color")
    status_filter = request.args.getlist("status")
    search_query = request.args.get("search", None)
    sort_option = request.args.get("sort", "name")
    page = request.args.get("page", 1, type=int)
    per_page = 10

    query = InstanceBike.query.join(Bike)

    # Apply filters
    if brand_filter:
        query = query.filter(Bike.brand.in_(brand_filter))
    if model_filter:
        query = query.filter(Bike.model.in_(model_filter))
    if frame_material_filter:
        query = query.filter(Bike.frame_material.in_(frame_material_filter))
    if brake_type_filter:
        query = query.filter(Bike.brake_type.in_(brake_type_filter))
    if size_filter:
        query = query.filter(InstanceBike.size.in_(size_filter))
    if color_filter:
        query = query.filter(InstanceBike.color.in_(color_filter))
    if status_filter:
        query = query.filter(InstanceBike.status.in_(status_filter))
    if search_query:
        query = query.filter(
            (Bike.model.ilike(f"%{search_query}%"))
            | (Bike.description.ilike(f"%{search_query}%"))
        )

    # Apply sorting
    if sort_option == "name":
        query = query.order_by(Bike.model)
    elif sort_option == "price":
        query = query.order_by(InstanceBike.price)  # Assuming `price` is a field
    elif sort_option == "availability":
        query = query.order_by(
            InstanceBike.status
        )  # Assuming status determines availability

    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    bike_instances = pagination.items  # Bikes for the current page
    total_pages = pagination.pages

    # Fetch filter options
    brands = [brand[0] for brand in db.session.query(Bike.brand).distinct().all()]
    models = [model[0] for model in db.session.query(Bike.model).distinct().all()]
    frame_materials = [material.value for material in FrameMaterialEnum]
    brake_types = [brake.value for brake in BrakeTypeEnum]
    sizes = [size.value for size in BikeSizeEnum]
    statuses = [status.value for status in BikeStatusEnum]
    colors = [
        color[0] for color in db.session.query(InstanceBike.color).distinct().all()
    ]

    return render_template(
        "rentals.jinja",
        title="Bike Instances",
        bike_instances=bike_instances,
        brands=brands,
        models=models,
        frame_materials=frame_materials,
        brake_types=brake_types,
        sizes=sizes,
        colors=colors,
        statuses=statuses,
        selected_filters={
            "brand": brand_filter,
            "model": model_filter,
            "frame_material": frame_material_filter,
            "brake_type": brake_type_filter,
            "size": size_filter,
            "color": color_filter,
            "status": status_filter,
            "search": search_query,
        },
        current_page=page,
        total_pages=total_pages,
        sort_option=sort_option,
        sort_options=[
            {"value": "name", "label": "Název"},
            {"value": "price", "label": "Cena"},
            {"value": "availability", "label": "Dostupnost"},
        ],
    )


@rentals_bp.route("/rentals-detail/<uuid:bike_instance_id>", methods=["GET", "POST"])
@jwt_required(optional=True)
def rentals_detail(bike_instance_id):
    bike_instance = InstanceBike.query.filter_by(id=bike_instance_id).join(Bike).first()

    if not bike_instance:
        flash("Bike instance not found.", "error")
        return redirect(url_for("rentals_bp.rentals")), 302

    if request.method == "POST":
        # Check if the user is logged in (JWT token verification)
        try:
            verify_jwt_in_request()  # This will raise an exception if JWT is not present or invalid
            user_id = get_jwt_identity()  # Retrieve the user ID from the JWT
        except Exception:
            flash("You must be logged in to make a reservation.", "error")
            return redirect(
                url_for("user_bp.login")
            )  # Redirect to login page if not logged in

        if bike_instance.status.value != "Available":
            flash("This bike is currently unavailable for reservation.", "error")
            return redirect(
                url_for("rentals_bp.rentals_detail", bike_instance_id=bike_instance.id)
            )

        try:
            reservation_start = request.form.get("reservation_start")
            reservation_end = request.form.get("reservation_end")

            # Validate dates
            try:
                reservation_start = datetime.strptime(
                    reservation_start, "%Y-%m-%dT%H:%M"
                )
                reservation_end = datetime.strptime(reservation_end, "%Y-%m-%dT%H:%M")
            except ValueError:
                flash("Invalid date format. Please try again.", "error")
                return redirect(
                    url_for(
                        "rentals_bp.rentals_detail", bike_instance_id=bike_instance.id
                    )
                )

            if reservation_start >= reservation_end:
                flash("End time must be after start time.", "error")
                return redirect(
                    url_for(
                        "rentals_bp.rentals_detail", bike_instance_id=bike_instance.id
                    )
                )

            if reservation_start < datetime.now():
                flash("Reservation start time cannot be in the past.", "error")
                return redirect(
                    url_for(
                        "rentals_bp.rentals_detail", bike_instance_id=bike_instance.id
                    )
                )

            # Create the reservation
            new_reservation = Reservation(
                reservation_start=reservation_start,
                reservation_end=reservation_end,
                ready_to_pickup=True,
                User_id=user_id,
                Instance_Bike_id=bike_instance.id,
            )

            # Update bike status to Rented
            bike_instance.status = BikeStatusEnum.Rented

            # Add to session and commit
            db.session.add(new_reservation)
            db.session.commit()

            flash("Reservation created successfully!", "success")
            return redirect(
                url_for("rentals_bp.rentals_detail", bike_instance_id=bike_instance.id)
            )

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while processing your reservation: {e}", "error")
            return redirect(
                url_for("rentals_bp.rentals_detail", bike_instance_id=bike_instance.id)
            )

    try:
        csrf_token = get_jwt()["csrf"]
    except Exception:
        csrf_token = generate_csrf()

    barcode_svg = generate_barcode_svg(bike_instance.id)

    barcode_svg_str = (
        barcode_svg.decode("utf-8") if isinstance(barcode_svg, bytes) else barcode_svg
    )

    bike_instance_with_barcode = {
        "bike_instance": bike_instance,
        "barcode_svg": barcode_svg_str,
    }

    return render_template(
        "bike_detail.jinja",
        title="Bike Detail",
        bike_instance=bike_instance_with_barcode,
        csrf_token=csrf_token,
    )


@rentals_bp.route("/rental", methods=["GET", "POST"])
@jwt_required()
def rent_checkout():
    get_jwt_identity()

    if is_admin_or_employee():
        return redirect(url_for("home_bp.home"))

    if request.method == "POST" and "reservation_id" in request.form:
        reservation_id = request.form.get("reservation_id")
        reservation = Reservation.query.get(reservation_id)

        if not reservation or not reservation.ready_to_pickup:
            flash("Reservation not found or not ready for pickup.", "error")
            return redirect(url_for("rentals_bp.rent_checkout"))

        rental = Rental(
            User_id=reservation.User_id,
            Instance_Bike_id=reservation.Instance_Bike_id,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            total_price=0,
        )

        try:
            db.session.add(rental)

            # Update reservation status to not ready for pickup
            reservation.ready_to_pickup = False  # Set the ready_to_pickup to False
            db.session.add(
                reservation
            )  # Add the updated reservation object to the session

            # Update the status of the bike to rented
            instance_bike = InstanceBike.query.get(reservation.Instance_Bike_id)
            instance_bike.status = BikeStatusEnum.Rented
            db.session.commit()

            flash("Rental successfully created!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating rental: {str(e)}", "error")

        return redirect(url_for("rentals_bp.rent_checkout"))

    if request.method == "POST" and "rental_id" in request.form:
        rental_id = request.form.get("rental_id")
        comments = request.form.getlist("comments[]")  # Fetch all comments
        rental = Rental.query.get(rental_id)

        if not rental:
            flash("Rental not found.", "error")
            return redirect(url_for("rentals_bp.rent_checkout"))

        end_time = datetime.utcnow()

        duration = (end_time - rental.start_time).total_seconds() / 3600

        # Correctly fetch the price object
        price = rental.instance_bike.bike.price

        if not price:
            flash("Price not found.", "error")
            return redirect(url_for("rentals_bp.rent_checkout"))

        # Calculate total price based on duration
        if duration < 24:
            total_price = round(duration * price.price_per_hour)
        else:
            total_price = round((duration / 24) * price.price_per_day)

        rental.end_time = end_time
        rental.total_price = total_price

        try:
            # Loop through the comments and create an inspection for each
            for comment in comments:
                if comment:
                    inspection = Inspection(
                        Rental_id=rental.id,  # Correct field name here
                        User_id=rental.User_id,  # Ensure you use the correct field name
                        comments=comment,
                    )
                    db.session.add(inspection)
                else:
                    instance_bike = InstanceBike.query.get(rental.Instance_Bike_id)
                    instance_bike.status = "Available"

            db.session.commit()
            flash("Rental updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating rental or creating inspection: {str(e)}", "error")

        return redirect(url_for("rentals_bp.rent_checkout"))

    reservations = Reservation.query.filter_by(ready_to_pickup=True).all()
    rentals_to_update = Rental.query.filter(Rental.end_time == Rental.start_time).all()

    csrf_token_from_jwt = get_jwt().get("csrf")

    reservations_with_barcode = []
    for reservation in reservations:
        barcode_svg = generate_barcode_svg(reservation.Instance_Bike_id)

        # Ensure the barcode SVG is a string
        barcode_svg_str = (
            barcode_svg.decode("utf-8")
            if isinstance(barcode_svg, bytes)
            else barcode_svg
        )

        reservations_with_barcode.append(
            {"reservation": reservation, "barcode_svg": barcode_svg_str}
        )

    rentals_to_update_with_barcode = []
    for rental in rentals_to_update:
        barcode_svg = generate_barcode_svg(rental.Instance_Bike_id)

        # Ensure the barcode SVG is a string
        barcode_svg_str = (
            barcode_svg.decode("utf-8")
            if isinstance(barcode_svg, bytes)
            else barcode_svg
        )

        rentals_to_update_with_barcode.append(
            {"rental": rental, "barcode_svg": barcode_svg_str}
        )

    return render_template(
        "rent_back_bike.jinja",
        title="Reservations for Rental",
        reservations=reservations_with_barcode,
        rentals_to_update=rentals_to_update_with_barcode,
        csrf_token=csrf_token_from_jwt,
    )

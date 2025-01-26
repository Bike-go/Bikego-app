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

    query = InstanceBike.query.join(Bike)

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

    bike_instances = query.all()

    brands = db.session.query(Bike.brand).distinct().all()
    brands = [brand[0] for brand in brands]

    models = db.session.query(Bike.model).distinct().all()
    models = [model[0] for model in models]

    frame_materials = [material.value for material in FrameMaterialEnum]
    brake_types = [brake.value for brake in BrakeTypeEnum]
    sizes = [size.value for size in BikeSizeEnum]
    statuses = [status.value for status in BikeStatusEnum]

    colors = db.session.query(InstanceBike.color).distinct().all()
    colors = [color[0] for color in colors]

    return (
        render_template(
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
        ),
        200,
    )


@rentals_bp.route("/rentals-detail/<uuid:bike_instance_id>", methods=["GET", "POST"])
@jwt_required(optional=True)
def rentals_detail(bike_instance_id):
    bike_instance = InstanceBike.query.filter_by(id=bike_instance_id).join(Bike).first()

    if not bike_instance:
        return redirect(url_for("rentals_bp.rentals")), 301

    if request.method == "POST":
        try:
            reservation_start = request.form.get("reservation_start")
            reservation_end = request.form.get("reservation_end")

            verify_jwt_in_request()
            user_id = get_jwt_identity()

            reservation_start = datetime.strptime(reservation_start, "%Y-%m-%d %H:%M")
            reservation_end = datetime.strptime(reservation_end, "%Y-%m-%d %H:%M")

            new_reservation = Reservation(
                reservation_start=reservation_start,
                reservation_end=reservation_end,
                ready_to_pickup=True,
                User_id=user_id,
                Instance_Bike_id=bike_instance.id,
            )

            db.session.add(new_reservation)
            db.session.commit()

            flash("Reservation created successfully!", "success")

            try:
                csrf_token = get_jwt()["csrf"]
            except Exception as e:
                csrf_token = generate_csrf()

            return (
                redirect(
                    url_for(
                        "rentals_bp.rentals_detail",
                        bike_instance_id=bike_instance.id,
                        csrf_token=csrf_token,
                    )
                ),
                301,
            )

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating reservation: {e}", "error")

    try:
        csrf_token = get_jwt()["csrf"]
    except Exception as e:
        csrf_token = generate_csrf()

    return (
        render_template(
            "bike_detail.jinja",
            title="Bike Detail",
            bike_instance=bike_instance,
            csrf_token=csrf_token,
        ),
        200,
    )


@rentals_bp.route("/rental", methods=["GET", "POST"])
@jwt_required()
def rent_checkout():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.role.value not in ["Admin", "Employee"]:
        return redirect(url_for("home_bp.home"))

    csrf_token_from_jwt = get_jwt().get("csrf")

    if request.method == "GET":
        reservations = Reservation.query.filter_by(ready_to_pickup=True).all()

        rentals_to_update = Rental.query.filter(
            Rental.end_time == Rental.start_time
        ).all()

        return (
            render_template(
                "rent_back_bike.jinja",
                title="Reservations for Rental",
                reservations=reservations,
                rentals_to_update=rentals_to_update,
                csrf_token=csrf_token_from_jwt,
            ),
            200,
        )

    if request.method == "POST" and "reservation_id" in request.form:
        reservation_id = request.form.get("reservation_id")
        reservation = Reservation.query.get(reservation_id)

        if not reservation or not reservation.ready_to_pickup:
            flash("Reservation not found or not ready for pickup.", "error")
            return redirect(url_for("rent_checkout"))

        rental = Rental(
            User_id=reservation.User_id,
            Instance_Bike_id=reservation.Instance_Bike_id,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            total_price=0,
        )

        try:
            db.session.add(rental)
            instance_bike = InstanceBike.query.get(reservation.Instance_Bike_id)
            instance_bike.status = BikeStatusEnum.Rented
            db.session.commit()
            flash("Rental successfully created!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating rental: {str(e)}", "error")

        return redirect(url_for("rent_checkout"))

    if request.method == "POST" and "rental_id" in request.form:
        rental_id = request.form.get("rental_id")
        end_time = request.form.get("end_time")
        comments = request.form.get("comments")
        rental = Rental.query.get(rental_id)

        if not rental:
            flash("Rental not found.", "error")
            return redirect(url_for("rent_checkout"))

        try:
            end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            flash("Invalid date format for end_time. Use YYYY-MM-DD HH:MM:SS.", "error")
            return redirect(url_for("rent_checkout"))

        duration = (end_time - rental.start_time).total_seconds() / 3600

        price = Price.query.first()

        if not price:
            flash("Price not found.", "error")
            return redirect(url_for("rent_checkout"))

        if duration < 24:
            total_price = round(duration * price.price_per_hour)
        else:
            total_price = round((duration / 24) * price.price_per_day)

        rental.end_time = end_time
        rental.total_price = total_price

        try:
            if comments:
                inspection = Inspection(
                    rental_id=rental.id, User_id=rental.User_id, comments=comments
                )
                db.session.add(inspection)

            db.session.commit()
            flash("Rental updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating rental or creating inspection: {str(e)}", "error")

        return redirect(url_for("rent_checkout"))

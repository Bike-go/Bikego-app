from flask import Blueprint, flash, request, render_template, redirect, url_for
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
from flask_wtf.csrf import generate_csrf
from models.bike_model import Bike, BrakeTypeEnum, FrameMaterialEnum
from models.category_model import Category
from models.instance_bike_model import BikeSizeEnum, BikeStatusEnum, InstanceBike
from models.news_model import News
from models.reservation_model import Reservation
from models.user_model import User, UserRoleEnum
from utils.barcode import generate_barcode_svg
from utils.statiscits import create_bar_chart, create_donut_chart
from utils.validator_utils import is_admin
from sqlalchemy.exc import SQLAlchemyError
from db import db

admin_bp = Blueprint("admin_bp", __name__)


@admin_bp.route("/admin", methods=["GET"])
@jwt_required()
def admin():
    get_jwt_identity()
    if is_admin():  # Corrected the logic
        return redirect(url_for("home_bp.home"))

    # Pagination for news (unchanged)
    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)

    total_news_count = News.query.count()
    news_items = (
        News.query.order_by(News.created_at.desc()).offset(offset).limit(limit).all()
    )

    # Calculate pagination data
    current_page = (offset // limit) + 1
    total_pages = (total_news_count + limit - 1) // limit  # Ceiling division

    # Query to join InstanceBike with Bike for the table
    instance_bikes = (
        db.session.query(InstanceBike, Bike)
        .join(Bike, InstanceBike.Bike_id == Bike.id)
        .order_by(InstanceBike.purchase_date.desc())
        .all()
    )

    instance_bikes_with_barcode = []
    for instance, bike in instance_bikes:
        barcode_svg = generate_barcode_svg(instance.id)

        # Ensure the barcode SVG is a string
        barcode_svg_str = (
            barcode_svg.decode("utf-8")
            if isinstance(barcode_svg, bytes)
            else barcode_svg
        )

        # Append a tuple of instance and barcode_svg
        instance_bikes_with_barcode.append((instance, bike, barcode_svg_str))

    users = User.query.order_by(User.created_at.desc()).all()

    try:
        csrf_token = get_jwt()[
            "csrf"
        ]  # This line assumes that CSRF token is stored in the JWT
    except Exception:
        csrf_token = (
            generate_csrf()
        )  # Fallback to generate CSRF token if not available in JWT

    # Query User data for roles
    user_roles_count = (
        db.session.query(User.role, db.func.count(User.id)).group_by(User.role).all()
    )

    # Convert Enum values to their string representation (value) for JSON serialization
    user_roles_count = [(role.name, count) for role, count in user_roles_count]

    # Query Bike data for categories
    bike_category_count = (
        db.session.query(Category.name, db.func.count(Bike.id))
        .join(Bike)
        .group_by(Category.name)
        .all()
    )

    # Query Reservation data by user
    reservations_by_user = (
        db.session.query(User.username, db.func.count(Reservation.id))
        .join(Reservation)
        .group_by(User.username)
        .all()
    )

    user_role_donut_chart = create_donut_chart(user_roles_count, "Users by Role")
    bike_category_donut_chart = create_donut_chart(
        bike_category_count, "Bikes by Category"
    )
    reservation_bar_chart = create_bar_chart(
        reservations_by_user, "Reservations by User"
    )

    return render_template(
        "admin_page.jinja",
        title="Admin",
        page="admin",
        users=users,
        news_items=news_items,
        instance_bikes=instance_bikes_with_barcode,
        csrf_token=csrf_token,
        current_page=current_page,
        total_pages=total_pages,
        limit=limit,
        FrameMaterialEnum=FrameMaterialEnum,
        BrakeTypeEnum=BrakeTypeEnum,
        BikeSizeEnum=BikeSizeEnum,
        BikeStatusEnum=BikeStatusEnum,
        user_role_donut_chart=user_role_donut_chart,
        bike_category_donut_chart=bike_category_donut_chart,
        reservation_bar_chart=reservation_bar_chart,
    )


@admin_bp.route("/manage_users", methods=["POST"])
@jwt_required()
def manage_users():
    user_id = get_jwt_identity()
    admin_user = User.query.get(user_id)
    if not admin_user or admin_user.role.value not in ["Admin"]:
        return redirect(url_for("home_bp.home"))

    action = request.form.get("action")
    user_id = request.form.get("user_id")
    user = User.query.get(user_id)

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("admin_bp.admin"))

    if action == "edit":
        user.username = request.form.get("username", user.username)
        user.email = request.form.get("email", user.email)
        user.phone_number = request.form.get("phone_number", user.phone_number)
        role = request.form.get("role", user.role)
        if role in UserRoleEnum.__members__:
            user.role = UserRoleEnum[role]

        try:
            db.session.commit()
            flash("User updated successfully!", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Error updating user: {str(e)}", "error")

    elif action == "delete":
        try:
            db.session.delete(user)
            db.session.commit()
            flash("User deleted successfully!", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Error deleting user: {str(e)}", "error")

    return redirect(url_for("admin_bp.admin"))


@admin_bp.route("/manage_bikes", methods=["POST"])
@jwt_required()
def manage_bikes():
    user_id = get_jwt_identity()
    admin_user = User.query.get(user_id)
    if not admin_user or admin_user.role.value != "Admin":
        flash("You do not have permission to manage bikes.", "error")
        return redirect(url_for("home_bp.home"))

    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "edit_instance":
                instance_id = request.form.get("instance_id")
                instance = InstanceBike.query.get(instance_id)
                if instance:
                    instance.size = BikeSizeEnum[request.form["size"]]
                    instance.color = request.form["color"]
                    instance.status = BikeStatusEnum[request.form["status"]]
                    db.session.commit()
                    flash("Instance updated successfully!", "success")
                else:
                    flash("Instance not found.", "error")

            elif action == "delete_instance":
                instance_id = request.form.get("instance_id")
                instance = InstanceBike.query.get(instance_id)
                if instance:
                    db.session.delete(instance)
                    db.session.commit()
                    flash("Instance deleted successfully!", "success")
                else:
                    flash("Instance not found.", "error")

            elif action == "create":
                # Create a new bike
                model = request.form["model"]
                frame_material = FrameMaterialEnum[request.form["frame_material"]]
                brake_type = BrakeTypeEnum[request.form["brake_type"]]
                brand = request.form["brand"]
                description = request.form["description"]
                category_id = request.form["Category_id"]
                price_id = request.form["Price_id"]
                instance_count = int(request.form["instance_count"])
                size = BikeSizeEnum[request.form["size"]]
                color = request.form["color"]

                new_bike = Bike(
                    model=model,
                    frame_material=frame_material,
                    brake_type=brake_type,
                    brand=brand,
                    description=description,
                    Category_id=category_id,
                    Price_id=price_id,
                )
                db.session.add(new_bike)
                db.session.flush()  # Ensures new_bike.id is available

                # Create instance bikes
                for _ in range(instance_count):
                    new_instance = InstanceBike(
                        size=size,
                        color=color,
                        Bike_id=new_bike.id,
                    )
                    db.session.add(new_instance)

                db.session.commit()
                flash("Bike and its instances created successfully!", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "error")

        return redirect(url_for("admin_bp.admin"))

    return redirect(url_for("admin_bp.admin"))

from flask import Blueprint, flash, request, render_template, redirect, url_for
from flask_jwt_extended import get_jwt, jwt_required, get_jwt_identity
from flask_wtf.csrf import generate_csrf
import db
from models.bike_model import Bike, BrakeTypeEnum, FrameMaterialEnum
from models.instance_bike_model import BikeSizeEnum, InstanceBike
from models.news_model import News
from models.user_model import User, UserRoleEnum
from utils.validator_utils import is_admin
from sqlalchemy.exc import SQLAlchemyError

admin_bp = Blueprint("admin_bp", __name__)


@admin_bp.route("/admin", methods=["GET"])
@jwt_required()
def admin():
    get_jwt_identity()
    if is_admin():
        return redirect(url_for("home_bp.home"))

    # Pagination for news
    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)

    total_news_count = News.query.count()
    news_items = (
        News.query.order_by(News.created_at.desc()).offset(offset).limit(limit).all()
    )

    # Calculate pagination data
    current_page = (offset // limit) + 1
    total_pages = (
        total_news_count + limit - 1
    ) // limit  # Ceiling division for total pages

    users = User.query.order_by(User.created_at.desc()).all()
    bikes = InstanceBike.query.all()

    try:
        csrf_token = get_jwt()["csrf"]
    except Exception as e:
        csrf_token = generate_csrf()

    return (
        render_template(
            "admin_page.jinja",
            title="Admin",
            page="admin",
            users=users,
            news_items=news_items,
            bikes=bikes,
            csrf_token=csrf_token,
            current_page=current_page,
            total_pages=total_pages,
            limit=limit,
        ),
        200,
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


@admin_bp.route("/manage_bikes", methods=["GET", "POST"])
@jwt_required()
def manage_bikes():
    user_id = get_jwt_identity()
    admin_user = User.query.get(user_id)
    if not admin_user or admin_user.role.value != "Admin":
        return redirect(url_for("home_bp.home"))

    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            # Create a new bike
            model = request.form.get("model")
            frame_material = request.form.get("frame_material")
            brake_type = request.form.get("brake_type")
            brand = request.form.get("brand")
            description = request.form.get("description")
            category_id = request.form.get("category_id")
            price_id = request.form.get("price_id")

            new_bike = Bike(
                model=model,
                frame_material=FrameMaterialEnum[frame_material],
                brake_type=BrakeTypeEnum[brake_type],
                brand=brand,
                description=description,
                Category_id=category_id,
                Price_id=price_id,
            )
            db.session.add(new_bike)
            db.session.commit()
            flash("Bike created successfully!", "success")

        elif action == "edit":
            bike_id = request.form.get("bike_id")
            bike = Bike.query.get(bike_id)
            if bike:
                bike.model = request.form.get("model", bike.model)
                bike.frame_material = FrameMaterialEnum[
                    request.form.get("frame_material", bike.frame_material.name)
                ]
                bike.brake_type = BrakeTypeEnum[
                    request.form.get("brake_type", bike.brake_type.name)
                ]
                bike.brand = request.form.get("brand", bike.brand)
                bike.description = request.form.get("description", bike.description)
                bike.Category_id = request.form.get("category_id", bike.Category_id)
                bike.Price_id = request.form.get("price_id", bike.Price_id)

                db.session.commit()
                flash("Bike updated successfully!", "success")
            else:
                flash("Bike not found.", "error")

        elif action == "delete":
            bike_id = request.form.get("bike_id")
            bike = Bike.query.get(bike_id)
            if bike:
                db.session.delete(bike)
                db.session.commit()
                flash("Bike deleted successfully!", "success")
            else:
                flash("Bike not found.", "error")

        return redirect(url_for("admin_bp.manage_bikes"))

    # Fetch bikes to display in template
    bikes = Bike.query.all()
    return render_template("manage_bikes.html", bikes=bikes)


@admin_bp.route("/manage_instance_bikes", methods=["GET", "POST"])
@jwt_required()
def manage_instance_bikes():
    user_id = get_jwt_identity()
    admin_user = User.query.get(user_id)
    if not admin_user or admin_user.role.value != "Admin":
        return redirect(url_for("home_bp.home"))

    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            bike_id = request.form.get("bike_id")
            size = request.form.get("size")
            color = request.form.get("color")
            new_instance = InstanceBike(
                size=BikeSizeEnum[size], color=color, Bike_id=bike_id
            )
            db.session.add(new_instance)
            db.session.commit()
            flash("Instance created successfully!", "success")

        elif action == "edit":
            instance_id = request.form.get("instance_id")
            instance = InstanceBike.query.get(instance_id)
            if instance:
                instance.size = request.form.get("size", instance.size)
                instance.color = request.form.get("color", instance.color)

                db.session.commit()
                flash("Instance updated successfully!", "success")
            else:
                flash("Instance not found.", "error")

        elif action == "delete":
            instance_id = request.form.get("instance_id")
            instance = InstanceBike.query.get(instance_id)
            if instance:
                db.session.delete(instance)
                db.session.commit()
                flash("Instance deleted successfully!", "success")
            else:
                flash("Instance not found.", "error")

        return redirect(url_for("admin_bp.manage_instance_bikes"))

    # Fetch instance bikes to display in template
    instance_bikes = InstanceBike.query.all()
    return render_template("manage_instance_bikes.html", instance_bikes=instance_bikes)

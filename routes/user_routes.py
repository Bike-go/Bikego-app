from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from models.user_model import User
from schemas import user_schema
from utils.email_utils import send_refresh_password_email, send_verification_email
from utils.imgur_utils import delete_image_from_imgur, upload_image_to_imgur
from utils.validator_utils import is_non_empty_string, is_valid_email, is_valid_password
from db import db

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("register.jinja")

    data = request.form
    user_data = user_schema.UserSignupSchema().load(data)


    if not (is_non_empty_string(user_data['email']) and is_valid_email(user_data['email'])):
        flash("Invalid email format.", "error")
        return redirect(url_for("user_bp.signup"))
    if not (is_non_empty_string(user_data['username'])):
        flash("Username cannot be empty.", "error")
        return redirect(url_for("user_bp.signup"))
    if not (is_valid_password(user_data['password0'])):
        flash("Password must be at least 8 characters long.", "error")
        return redirect(url_for("user_bp.signup"))
    if user_data['password0'] != user_data['password1']:
        flash("Passwords do not match.", "error")
        return redirect(url_for("user_bp.signup"))
    
    existing_user = User.query.filter_by(email=user_data['email']).first()
    if existing_user:
        flash("Email already registered!", "danger")
        return redirect(url_for('register'))
 
    new_user = User(
        username=user_data['username'],
        password_hash=generate_password_hash(user_data['password0']),
        email=user_data['email'],
        created_at=datetime.utcnow(),
        role='Customer',
        email_verified=False,
        darkmode=False
    )

    db.session.add(new_user)
    db.session.commit()

    # Generate email verification token valid for 15 minutes
    token = create_access_token(identity=new_user.id, expires_delta=timedelta(minutes=15))
    
    # Send verification email
    send_verification_email(new_user.email, token)

    flash("User created successfully. Please verify your email.", "success")
    return redirect(url_for("user_bp.login"))

# Login
@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    data = request.form
    email_or_username = data.get("email_or_username")
    password = data.get("password")

    if not is_non_empty_string(email_or_username):
        flash("Email or username cannot be empty.", "error")
        return redirect(url_for("user_bp.login"))
    if not is_valid_password(password):
        flash("Password must be at least 8 characters long.", "error")
        return redirect(url_for("user_bp.login"))

    # Check if the input is an email
    user = None
    if "@" in email_or_username:
        user = User.query.filter_by(email=email_or_username).first()
    else:
        user = User.query.filter_by(username=email_or_username).first()

    if user and check_password_hash(user.password_hash, password):
        # Update last_login timestamp
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Create access and refresh tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # Store tokens in session (or cookies)
        flash("Login successful.", "success")
        return redirect(url_for("user_bp.dashboard"))

    flash("Invalid credentials.", "error")
    return redirect(url_for("user_bp.login"))

# Dashboard (Example)
@user_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("user_bp.login"))

    return render_template("dashboard.html", user=user)

# Change password
@user_bp.route("/change-password/<token>", methods=["GET", "POST"])
def change_password(token):
    if request.method == "GET":
        return render_template("change_password.html")

    data = request.form
    password0 = data.get("password0")
    password1 = data.get("password1")

    if not password0 or not password1:
        flash("Both password fields are required.", "error")
        return redirect(request.url)
    if not is_valid_password(password0):
        flash("Password must be at least 8 characters long.", "error")
        return redirect(request.url)
    if password0 != password1:
        flash("Passwords do not match.", "error")
        return redirect(request.url)

    # Decode the token to get the user ID
    try:
        user_id = get_jwt_identity(token)
    except Exception:
        flash("Invalid or expired token.", "error")
        return redirect(url_for("user_bp.login"))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("user_bp.login"))

    # Update the user's password
    user.password_hash = generate_password_hash(password0)
    db.session.commit()

    flash("Password changed successfully.", "success")
    return redirect(url_for("user_bp.login"))

# Profile (View/Edit User Data)
@user_bp.route("/me", methods=["GET", "POST"])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("user_bp.login"))

    if request.method == "POST":
        data = request.form
        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)
        user.phone_number = data.get("phone_number", user.phone_number)
        user.darkmode = data.get("darkmode") == "on"

        db.session.commit()
        flash("Profile updated successfully.", "success")

    return render_template("profile.html", user=user)
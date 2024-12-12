from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token, jwt_required, get_jwt_identity, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from marshmallow import ValidationError
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from models.bike_model import Bike
from models.instance_bike_model import InstanceBike
from models.rental_model import Rental
from models.reservation_model import Reservation
from models.review_model import Review
from models.user_model import User
from schemas import user_schema
from utils.block_authenticated import block_authenticated
from utils.email_utils import send_password_change, send_registration_email, send_reset_email, send_successfully_password_change
from utils.imgur_utils import delete_image_from_imgur, upload_image_to_imgur
from utils.validator_utils import is_valid_email, is_valid_password, is_valid_phone_number
from db import db

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/signup", methods=["GET", "POST"])
@block_authenticated
def signup():
    if request.method == "GET":
        return render_template("signup.jinja", title="Registrace", page="signup")

    data = request.form
    try:
        user_data = user_schema.UserSignupSchema().load(data)
    except ValidationError as e:
        flash(f"Validation error: {e.messages}", "error")
        return render_template("signup.jinja", title="Registrace", page="signup", form_data=data)

    if not is_valid_email(user_data.get('email', '')):
        flash("Invalid email format.", "error")
        return render_template("signup.jinja", title="Registrace", page="signup", form_data=data)

    if user_data['password0'] != user_data['password1']:
        flash("Passwords do not match.", "error")
        return render_template("signup.jinja", title="Registrace", page="signup", form_data=data)

    # Check for existing email or username
    existing_user = User.query.filter(
        (User.email == user_data['email']) | (User.username == user_data['username'])
    ).first()
    if existing_user:
        flash("Email or Username already exists!", "danger")
        return render_template("signup.jinja", title="Registrace", page="signup", form_data=data)

    # Create new user
    new_user = User(
        username=user_data['username'],
        password_hash=generate_password_hash(user_data['password0']),
        email=user_data['email'],
        created_at=datetime.utcnow(),
        role='Customer',
        email_verified=False,
        darkmode=False,
    )

    db.session.add(new_user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Error saving user: {e}", "error")
        return render_template("signup.jinja", title="Registrace", page="signup", form_data=data)

    # Generate verification token
    token = create_access_token(identity=new_user.id, expires_delta=timedelta(minutes=60))

    # Send email
    try:
        send_registration_email(new_user.email, token)
        flash("User created successfully. Please verify your email.", "success")
    except Exception as e:
        flash(f"Error sending verification email: {e}", "error")
        return redirect(url_for("user_bp.signup"))

    return redirect(url_for("user_bp.login"))

# Verify email
@user_bp.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    try:
        # Decode the token
        decoded_token = decode_token(token)
        user_id = decoded_token.get("sub")  # Extract the user ID from the token
        
        # Fetch the user from the database
        user = User.query.filter_by(id=user_id).first()
        if not user:
            flash("Invalid or expired token.", "error")
            return redirect(url_for("user_bp.login"))

        # Check if the email is already verified
        if user.email_verified:
            flash("Email is already verified.", "info")
            return redirect(url_for("user_bp.login"))

        # Mark the email as verified
        user.email_verified = True
        db.session.commit()

        # Send a welcome email
        try:
            send_successfully_password_change(user.email)
        except Exception as e:
            flash(f"Email verified, but failed to send welcome email: {e}", "warning")

        flash("Email verified successfully.", "success")
    except Exception as e:
        flash("Invalid or expired token.", "error")
        return redirect(url_for("user_bp.login"))

    return redirect(url_for("user_bp.login"))

# Login
@user_bp.route("/login", methods=["GET", "POST"])
@block_authenticated
def login():
    if request.method == "GET":
        return render_template("login.jinja", title="Přihlášení", page="login")

    # Get form data
    data = user_schema.UserLoginSchema().load(request.form)
    username_or_email = data.get("username")
    password = data.get("password0")

    # Validate inputs
    if not username_or_email or not password:
        flash("Email/username and password cannot be empty.", "error")
        return redirect(url_for("user_bp.login"))

    # Determine if the input is an email or username (case-insensitive)
    user = None
    if "@" in username_or_email:
        user = User.query.filter(User.email.ilike(username_or_email)).first()
    else:
        user = User.query.filter(User.username.ilike(username_or_email)).first()

    # Verify user credentials
    if user and check_password_hash(user.password_hash, password):
        if not user.email_verified:
            flash("Please verify your email before logging in.", "warning")
            return redirect(url_for("user_bp.login"))

        # Update last_login timestamp
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Create the tokens we will be sending back to the user
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # Set the JWT cookies in the response
        response = redirect(url_for("home"))
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        flash("Login successful.", "success")
        return response

    flash("Login failed. Please try again.", "error")
    return redirect(url_for("user_bp.login"))

# Send password reset email
@user_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgot_password.jinja", title="Obnovení hesla", page="forgot_password")
    
    email = user_schema.SendResetPasswordEmailSchema().load(request.form).get("email")

    # Validate email format
    if not is_valid_email(email):
        flash("Invalid email format.", "error")
        return redirect(url_for("user_bp.forgot_password"))

    # Prevent enumeration attacks by not revealing user existence
    user = User.query.filter_by(email=email).first()
    if user:
        # Generate token valid for 15 minutes
        token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=60))
        
        # Send password reset email
        try:
            send_password_change(user.email, token)
        except Exception as e:
            flash("An error occurred while sending the reset email. Please try again later.", "error")
            return redirect(url_for("user_bp.forgot_password"))

    # Generic success message
    flash("If the email is associated with an account, a reset link has been sent.", "success")
    return redirect(url_for("user_bp.login"))

# Change password
@user_bp.route("/change-password/<token>", methods=["GET", "POST"])
def change_password(token):
    if request.method == "GET":
        return render_template("change_password.jinja", title="Obnovení hesla", page="change_password")

    data = user_schema.ChangePasswordSchema().load(request.form)
    password0 = data.get("password0")
    password1 = data.get("password1")

    # Validate password inputs
    if not password0 or not password1:
        flash("Both password fields are required.", "error")
        return redirect(request.url)
    if not is_valid_password(password0):  # Assuming this checks length, complexity, etc.
        flash("Password must meet the security requirements.", "error")
        return redirect(request.url)
    if password0 != password1:
        flash("Passwords do not match.", "error")
        return redirect(request.url)

    # Decode the token to extract the user ID
    try:
        decoded_token = decode_token(token)
        user_id = decoded_token["sub"]
    except Exception as e:
        flash("Invalid or expired token. Please request a new password reset.", "error")
        return redirect(url_for("user_bp.forgot_password"))

    # Fetch the user
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("user_bp.login"))

    # Update the user's password
    user.password_hash = generate_password_hash(password0)
    db.session.commit()

    flash("Password changed successfully. You can now log in with your new password.", "success")
    return redirect(url_for("user_bp.login"))

# Logout
@user_bp.route('/logout', methods=['POST'])
def logout():
    response = jsonify({'message': 'Logged out successfully'})
    unset_jwt_cookies(response)
    return redirect(url_for("home")), 200

@user_bp.route("/delete-user", methods=["POST"])  # Accept only POST requests
@jwt_required()  # Ensure the user is authenticated
def delete_user():
    # Get the current user ID from the JWT identity
    current_user_id = get_jwt_identity()
    if not current_user_id:
        flash("User not found.", "error")
        return redirect(url_for("user_bp.settings"))

    user = User.query.get(current_user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("user_bp.settings"))

    # Retrieve password from the form
    password = request.form.get("password")
    if not password:
        flash("Password is required to delete your account.", "error")
        return redirect(url_for("user_bp.settings"))

    # Check if the provided password matches
    if not check_password_hash(user.password_hash, password):
        flash("Password is incorrect.", "error")
        return redirect(url_for("user_bp.settings"))

    # Clear user data (except for the ID)
    user.username = ""
    user.password_hash = ""
    user.email = ""
    user.phone_number = ""
    user.last_login = None
    user.profile_picture_url = ""
    user.delete_hash = ""
    user.email_verified = False
    user.darkmode = False

    # Commit changes to the database
    db.session.commit()

    # Clear JWT cookies
    response = redirect(url_for("user_bp.login"))  # Prepare redirect response
    unset_jwt_cookies(response)  # Clear JWT cookies from the response

    flash("Your account has been deleted successfully.", "success")
    return response

@user_bp.route("/profile", methods=["GET", "POST"])
@jwt_required()
def profile():
    # Get the current user's ID and role from the JWT token
    current_user_id = get_jwt_identity()

    # Query the database to find the user by the extracted ID
    user = User.query.get(current_user_id)

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("user_bp.login"))

    # Dynamically select the schema based on the user's role
    if user.role.value == "Admin":
        user_schema_instance = user_schema.AdminUserSchema()
    else:
        user_schema_instance = user_schema.RegularUserSchema()

    # Query Total Reservation Time
    total_time = (
        db.session.query(func.sum(Reservation.reservation_end - Reservation.reservation_start).label('total_time'))
        .filter(Reservation.User_id == user.id)
        .scalar()
    )

    if not total_time:
        total_time = timedelta(0)

    # Query Favourite Bike
    favourite_bike = (
        db.session.query(Bike.model)
        .join(InstanceBike, InstanceBike.Bike_id == Bike.id)  # Explicit join condition
        .join(Reservation, Reservation.Instance_Bike_id == InstanceBike.id)  # Explicit join condition
        .filter(Reservation.User_id == user.id)  # Filter by User ID
        .group_by(Bike.model)  # Group by Bike model
        .order_by(func.count(Reservation.id).desc())  # Order by count of reservations
        .limit(1)  # Limit to 1 result
        .first()  # Get the first result
    )

    if not favourite_bike:
        favourite_bike = "No favourite bike"

    # Query Active Sessions (Reservations that are not finished yet)
    active_sessions = (
        db.session.query(Reservation, InstanceBike)
        .join(InstanceBike, Reservation.Instance_Bike_id == InstanceBike.id)  # Explicit join condition
        .filter(Reservation.User_id == user.id, Reservation.reservation_end > datetime.utcnow())  # Filter by User ID and active reservations
        .all()
    )

    if not active_sessions:
        active_sessions = []

    # Query User Reviews
    reviews = (
        db.session.query(Review)
        .filter(Review.User_id == user.id)  # Filter by User ID
        .all()
    )

    if not reviews:
        reviews = []

    # Query Purchase History (Rentals)
    purchase_history = (
        db.session.query(Rental, InstanceBike)
        .join(InstanceBike, Rental.Instance_Bike_id == InstanceBike.id)  # Explicit join condition
        .filter(Rental.User_id == user.id)  # Filter by User ID
        .all()
    )

    if not purchase_history:
        purchase_history = []

    # Prepare data to render in the template
    user_data = user_schema_instance.dump(user)
    user_data["role"] = user.role.value

    if request.method == "POST":
        data = request.form

        try:
            # Deserialize and validate input data using the selected schema
            updated_data = user_schema_instance.load(data, partial=True)

            # Check for unique username
            if "username" in updated_data and updated_data["username"] != user.username:
                if User.query.filter_by(username=updated_data["username"]).first():
                    flash("Username is already taken.", "error")
                    pass

            # Check for unique email
            if "email" in updated_data and updated_data["email"] != user.email:
                if User.query.filter_by(email=updated_data["email"]).first():
                    flash("Email is already taken.", "error")
                    pass

                # If email changes, set email_verified to False and send verification email
                token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=60))
                send_reset_email(user.email, updated_data["email"], token)  # Implement email sending logic
                user.email_verified = False

            # Validate phone number using regex
            if "phone_number" in updated_data:
                if is_valid_phone_number(updated_data["phone_number"]):
                    flash("Invalid phone number format.", "error")
                    pass

            # Update the user object with the validated data
            for key, value in updated_data.items():
                setattr(user, key, value)

            # Handle profile picture update
            if "profile_image" in request.files:
                image_file = request.files["profile_image"]

                # Delete the old profile picture from Imgur if it exists
                if user.picture_delete_hash:
                    delete_image_from_imgur(user.picture_delete_hash)

                # Upload the new profile picture to Imgur
                profile_picture_url, delete_hash = upload_image_to_imgur(image_file)
                user.profile_picture_url = profile_picture_url
                user.picture_delete_hash = delete_hash

            # Save changes to the database
            db.session.commit()
            flash("Profile updated successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {e}", "error")

        # Re-render the profile page with updated user data
        user_data = user_schema_instance.dump(user)  # Serialize updated user object
        pass

    # For GET request, just render the profile page with serialized user data
    return render_template("profile.jinja", 
                           user=user_data, 
                           title="Profil", 
                           page="profile", 
                           total_time=total_time, 
                           favourite_bike=favourite_bike,
                           active_sessions=active_sessions,
                           reviews=reviews,
                           purchase_history=purchase_history)

@user_bp.route('/refresh_token', methods=['POST', 'GET'])
@jwt_required(refresh=True)
def refresh_token():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    response = jsonify({'refresh': True})
    set_access_cookies(response, access_token)
    return response, 200
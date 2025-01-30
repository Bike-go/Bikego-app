from flask import Blueprint, jsonify, request
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

# Sign up new users
@user_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    user_data, errors = user_schema.UserSignupSchema().load(data)

    if errors:
        return jsonify(errors), 400  # Return validation errors

    if not (is_non_empty_string(user_data['email']) and is_valid_email(user_data['email'])):
        return jsonify({"msg": "Invalid email format."}), 400
    if not (is_non_empty_string(user_data['username'])):
        return jsonify({"msg": "Username cannot be empty."}), 400
    if not (is_valid_password(user_data['password0'])):
        return jsonify({"msg": "Password must be at least 8 characters long."}), 400
    if user_data['password0'] != user_data['password1']:
        return jsonify({"msg": "Passwords do not match."}), 400

    new_user = User(
        username=user_data['username'],
        password_hash=generate_password_hash(user_data['password0']),
        email=user_data['email'],
        created_at=datetime.utcnow(),
        role='Customer',  # Default role
        email_verified=False,
        darkmode=False  # Default value
    )

    db.session.add(new_user)
    db.session.commit()

    # Generate email verification token valid for 15 minutes
    token = create_access_token(identity=new_user.id, expires_delta=timedelta(minutes=15))
    
    # Send verification email
    send_verification_email(new_user.email, token)

    return jsonify({"msg": "User created successfully. Please verify your email."}), 201

@user_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user_data, errors = user_schema.UserLoginSchema().load(data)

    if errors:
        return jsonify(errors), 400  # Return validation errors

    email_or_username = user_data['email_or_username']
    password = user_data['password']

    if not is_non_empty_string(email_or_username):
        return jsonify({"msg": "Email or username cannot be empty."}), 400
    if not is_valid_password(password):
        return jsonify({"msg": "Password must be at least 8 characters long."}), 400

    # Check if the input is an email
    user = None
    if "@" in email_or_username:
        user = User.query.filter_by(email=email_or_username).first()
    else:
        user = User.query.filter_by(username=email_or_username).first()

    if user and check_password_hash(user.password_hash, password):
        # Update last_login timestamp
        user.last_login = datetime.utcnow()  # Set current time as last login
        db.session.commit()  # Commit the change to the database

        # Create access and refresh tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "msg": "Login successful."
        }), 200

    return jsonify({"msg": "Invalid credentials."}), 401

@user_bp.route("/change-password/<token>", methods=["POST"])
def change_password(token):
    data = request.json
    password0 = data.get("password0")
    password1 = data.get("password1")

    if not password0 or not password1:
        return jsonify({"msg": "Both password fields are required."}), 400
    if not (is_valid_password(password0)):
        return jsonify({"msg": "Password must be at least 8 characters long."}), 400
    if password0 != password1:
        return jsonify({"msg": "Passwords do not match."}), 400

    # Decode the token to get the user ID
    try:
        user_id = get_jwt_identity(token)
    except Exception as e:
        return jsonify({"msg": "Invalid or expired token."}), 401

    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": "User not found."}), 404

    # Update the user's password
    user.password_hash = generate_password_hash(password0)
    db.session.commit()

    return jsonify({"msg": "Password changed successfully."}), 200

@user_bp.route("/send-password-change", methods=["POST"])
def send_password_change():
    data = request.json
    email = data.get("email")

    if not (is_non_empty_string(email) and is_valid_email(email)):
        return jsonify({"msg": "Invalid email format."}), 400

    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"msg": "User not found."}), 404

    # Create a special JWT token
    token = create_access_token(identity=user.id, expires_delta=datetime.timedelta(minutes=15))

    # Send the email
    send_refresh_password_email(email, token)

    return jsonify({"msg": "Password change email sent."}), 200

# Verify email for account activation
@user_bp.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if user:
            user.email_verified = True
            db.session.commit()
            return jsonify({"msg": "Email verified successfully."}), 200

        return jsonify({"msg": "Invalid verification token."}), 400
    except Exception as e:
        return jsonify({"msg": "Token has expired or is invalid."}), 400
    
# Refresh token
@user_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=user_id)
    return jsonify(access_token=new_access_token), 200

@user_bp.route("/me", methods=["GET"])
@jwt_required()
def get_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if user is None:
        return jsonify({"msg": "User not found."}), 404

    user_schema0 = user_schema.UserSchema()
    return user_schema0.jsonify(user), 200

@user_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if user is None:
        return jsonify({"msg": "User not found."}), 404

    data = request.json
    update_schema = user_schema.UpdateUserSchema()
    errors = update_schema.validate(data)

    if errors:
        return jsonify(errors), 400

    # Update user details
    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    user.phone_number = data.get("phone_number", user.phone_number)
    user.darkmode = data.get("darkmode", user.darkmode)

    db.session.commit()

    return jsonify({"msg": "User details updated successfully."}), 200

@user_bp.route("/me/delete/<string:password>", methods=["DELETE"])
@jwt_required()
def delete_user(password):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if user is None:
        return jsonify({"msg": "User not found."}), 404

    # Check if the provided password matches
    if not check_password_hash(password, user.password_hash):
        return jsonify({"msg": "Password is incorrect."}), 403

    # Clear user data (except for the ID)
    user.username = ""
    user.password_hash = ""
    user.email = ""
    user.phone_number = ""
    user.profile_picture_url = ""
    user.delete_hash = ""
    user.last_login = None
    user.email_verified = False
    user.darkmode = False
    user.role = None  # Assuming role can be null; change if necessary

    # Commit changes to the database
    db.session.commit()

    return jsonify({"msg": "User data cleared successfully."}), 200

@user_bp.route("/me/profile-image", methods=["POST"])
@jwt_required()
def upload_profile_image():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if user is None:
        return jsonify({"msg": "User not found."}), 404

    # Ensure a file is included in the request
    if "image" not in request.files:
        return jsonify({"msg": "No image file provided."}), 400

    image_file = request.files["image"]
    
    if image_file.filename == '':
        return jsonify({"msg": "No selected file."}), 400

    # Upload the image to Imgur
    try:
        image_url, delete_hash = upload_image_to_imgur(image_file)
        user.profile_picture_url = image_url
        user.delete_hash = delete_hash
        db.session.commit()
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

    return jsonify({"msg": "Profile image uploaded successfully.", "url": user.profile_picture_url}), 201

@user_bp.route("/me/profile-image", methods=["DELETE"])
@jwt_required()
def delete_profile_image():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if user is None:
        return jsonify({"msg": "User not found."}), 404

    if user.delete_hash is None:
        return jsonify({"msg": "No profile image to delete."}), 404

    # Delete the image from Imgur
    try:
        delete_image_from_imgur(user.delete_hash)
        user.profile_picture_url = None
        user.delete_hash = None
        db.session.commit()
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

    return jsonify({"msg": "Profile image deleted successfully."}), 200
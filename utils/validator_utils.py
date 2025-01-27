import re
from flask_jwt_extended import get_jwt_identity
from models.user_model import User


def is_valid_email(email):
    """Check if the provided email is valid."""
    return isinstance(email, str) and "@" in email


def is_valid_password(password):
    """Check if the provided password is valid (minimum length 8)."""
    return isinstance(password, str) and len(password) >= 8


def is_password_match(password, confirm_password):
    """Check if the provided password matches the confirm password."""
    return password == confirm_password


def is_valid_username(username):
    """Check if the provided username is valid (minimum length 3)."""
    return isinstance(username, str) and len(username) >= 3


def is_valid_phone_number(phone_number):
    """Check if the provided phone number is valid (minimum length 10)."""
    phone_regex = re.compile(r"^\+?[1-9]\d{1,14}$")
    return phone_regex.match(phone_number)


def is_admin_or_employee():
    """Check if the user is an admin or an employee."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    return current_user.role in ["Admin", "Employee"]


def is_admin_or_service():
    """Check if the user is an admin or a service provider."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    return current_user.role in ["Admin", "Service"]


def is_admin():
    """Check if the user is an admin."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    return current_user.role == "Admin"

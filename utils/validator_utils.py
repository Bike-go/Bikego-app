import re
from flask_jwt_extended import get_jwt_identity
from models.user_model import User

def is_valid_email(email):
    """Check if the provided email is valid."""
    return isinstance(email, str) and '@' in email

def is_valid_password(password):
    """Check if the provided password is valid (minimum length 8)."""
    return isinstance(password, str) and len(password) >= 8

def is_non_empty_string(value):
    """Check if the provided value is a non-empty string."""
    return isinstance(value, str) and len(value) > 0

def is_valid_phone_number(phone_number):
    """Check if the provided phone number is valid (minimum length 10)."""
    phone_regex = re.compile(r"^\+?[1-9]\d{1,14}$")
    return phone_regex.match(phone_number)

def is_admin_or_employee():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    return current_user.role in ['Admin', 'Employee']

def is_admin_or_employee(user):
    return user.role in ["Admin", "Employee"]

def is_user_role(role):
    current_user = get_jwt_identity()
    return current_user['role'] == role
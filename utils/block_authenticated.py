from functools import wraps
from flask import redirect, url_for, flash
from flask_jwt_extended import get_jwt_identity, jwt_required


def block_authenticated(f):
    @wraps(f)
    @jwt_required(optional=True)
    def decorated_function(*args, **kwargs):
        user_identity = get_jwt_identity()
        if user_identity:
            flash("You are already logged in.", "warning")
            return redirect(url_for("user_bp.profile"))
        return f(*args, **kwargs)

    return decorated_function

from flask import Blueprint, render_template

legal_notices_bp = Blueprint('legal_notices_bp', __name__)

@legal_notices_bp.route('/tos', methods=['GET'])
def tos():
    return render_template("terms_of_services.jinja", title="Terms of Service", page="tos"), 200

@legal_notices_bp.route('/privacy', methods=['GET'])
def privacy():
    return render_template("privacy_policy.jinja", title="Privacy Policy", page="privacy"), 200

@legal_notices_bp.route('/cookies', methods=['GET'])
def cookies():
    return render_template("cookies_policy.jinja", title="Cookies Policy", page="cookies"), 200
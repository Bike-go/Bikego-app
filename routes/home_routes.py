from flask import Blueprint, render_template

home_bp = Blueprint('home_bp', __name__)

@home_bp.route('/home', methods=['GET'])
def home():
    return render_template("home.jinja", title="Home", page="home"), 200
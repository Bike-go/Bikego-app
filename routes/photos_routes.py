from flask import Blueprint, render_template

photos_bp = Blueprint('photos_bp', __name__)

@photos_bp.route('/photos', methods=['GET'])
def photos():
    return render_template("photos.jinja", title="Photos", page="photos"), 200
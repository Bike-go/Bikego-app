from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.picture_model import Picture
from schemas.picture_schema import PictureSchema
from utils.imgur_utils import upload_image_to_imgur, delete_image_from_imgur
from db import db

picture_bp = Blueprint("picture_bp", __name__)

# Upload a new picture
@picture_bp.route("/pictures", methods=["POST"])
@jwt_required()
def create_picture():
    current_user = get_jwt_identity()
    if current_user["role"] not in ["Employee", "Admin"]:
        return jsonify({"msg": "Access forbidden"}), 403

    if "image" not in request.files:
        return jsonify({"msg": "No image file provided"}), 400

    image_file = request.files["image"]
    try:
        bike_picture_url, delete_hash = upload_image_to_imgur(image_file)
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

    json_data = request.form.to_dict()
    json_data["bike_picture_url"] = bike_picture_url
    json_data["picture_delete_hash"] = delete_hash

    try:
        picture_data = PictureSchema().load(json_data)
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

    picture = Picture(**picture_data)
    db.session.add(picture)
    db.session.commit()

    return PictureSchema().jsonify(picture), 201

# Get all pictures with pagination
@picture_bp.route("/pictures", methods=["GET"])
def get_pictures():
    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)
    
    # Query the database with limit and offset
    pictures = Picture.query.offset(offset).limit(limit).all()
    return PictureSchema(many=True).jsonify(pictures), 200

# Get a specific picture
@picture_bp.route("/pictures/<int:picture_id>", methods=["GET"])
@jwt_required()
def get_picture(picture_id):
    picture = Picture.query.get_or_404(picture_id)
    return PictureSchema().jsonify(picture), 200

# Update picture description
@picture_bp.route("/pictures/<int:picture_id>", methods=["PUT"])
@jwt_required()
def update_picture(picture_id):
    current_user = get_jwt_identity()
    if current_user["role"] not in ["Employee", "Admin"]:
        return jsonify({"msg": "Access forbidden"}), 403

    picture = Picture.query.get_or_404(picture_id)
    json_data = request.get_json()
    description = json_data.get("description")

    if description:
        picture.description = description
        db.session.commit()
        return PictureSchema().jsonify(picture), 200
    else:
        return jsonify({"msg": "Description is required"}), 400

# Delete a picture
@picture_bp.route("/pictures/<int:picture_id>", methods=["DELETE"])
@jwt_required()
def delete_picture(picture_id):
    current_user = get_jwt_identity()
    if current_user["role"] not in ["Employee", "Admin"]:
        return jsonify({"msg": "Access forbidden"}), 403

    picture = Picture.query.get_or_404(picture_id)
    try:
        delete_image_from_imgur(picture.picture_delete_hash)
    except Exception as e:
        return jsonify({"msg": str(e)}), 500

    db.session.delete(picture)
    db.session.commit()

    return jsonify({"msg": "Picture deleted successfully"}), 204
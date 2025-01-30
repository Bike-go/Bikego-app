from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models.category_model import Category
from schemas.category_schema import CategorySchema
from db import db

category_bp = Blueprint('category_bp', __name__)

# Create a new category
@category_bp.route("/categories", methods=["POST"])
@jwt_required()
def create_category():
    json_data = request.get_json()

    # Validate the request data
    if not json_data:
        return jsonify({"msg": "No input data provided"}), 400

    try:
        category_data = CategorySchema().load(json_data)
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

    category = Category(**category_data)
    db.session.add(category)
    db.session.commit()

    return CategorySchema().jsonify(category), 201

# Get a category by ID
@category_bp.route("/categories/<int:category_id>", methods=["GET"])
@jwt_required()
def get_category(category_id):
    category = Category.query.get_or_404(category_id)
    return CategorySchema().jsonify(category), 200

# Update an existing category
@category_bp.route("/categories/<int:category_id>", methods=["PUT"])
@jwt_required()
def update_category(category_id):
    json_data = request.get_json()
    category = Category.query.get_or_404(category_id)

    # Update category fields
    category.name = json_data.get("name", category.name)
    category.description = json_data.get("description", category.description)

    db.session.commit()

    return CategorySchema().jsonify(category), 200

# Delete a category
@category_bp.route("/categories/<int:category_id>", methods=["DELETE"])
@jwt_required()
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()

    return jsonify({"msg": "Category deleted."}), 204

# Get all categories with pagination
@category_bp.route("/categories", methods=["GET"])
def get_all_categories():
    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)
    
    categories = Category.query.limit(limit).offset(offset).all()
    return CategorySchema(many=True).jsonify(categories), 200
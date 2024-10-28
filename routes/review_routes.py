import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Review, user_model
from schemas import review_schema
from utils.validator_utils import is_admin_or_employee
from db import db

review_bp = Blueprint("review_bp", __name__)

# Create a Review (without publishing)
@review_bp.route("/reviews", methods=["POST"])
@jwt_required()
def create_review():
    data = request.get_json()
    user_id = get_jwt_identity()

    # Add user ID to the data
    data['user_id'] = user_id

    # Validate and deserialize input
    errors = review_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    new_review = Review(**data)
    db.session.add(new_review)
    db.session.commit()

    return review_schema.jsonify(new_review), 201

# Publish a Review (Admin/Employee Only)
@review_bp.route("/reviews/<int:review_id>/publish", methods=["PUT"])
@jwt_required()
def publish_review(review_id):
    user_id = get_jwt_identity()
    current_user = user_model.User().query.get(user_id)
    
    # Only Admins and Employees can publish reviews
    if not is_admin_or_employee(current_user):
        return jsonify({"msg": "Only admins or employees can publish reviews"}), 403

    review = Review.query.get_or_404(review_id)

    # Set the published_at field to current timestamp
    review.published_at = datetime.utcnow()
    db.session.commit()

    return review_schema.jsonify(review), 200

# Update a Review
@review_bp.route("/reviews/<int:review_id>", methods=["PUT"])
@jwt_required()
def update_review(review_id):
    data = request.get_json()
    review = Review.query.get_or_404(review_id)

    # Validate and deserialize input
    errors = review_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    # Update review fields
    for key, value in data.items():
        setattr(review, key, value)

    db.session.commit()
    return review_schema.jsonify(review), 200

# Delete a Review
@review_bp.route("/reviews/<int:review_id>", methods=["DELETE"])
@jwt_required()
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return jsonify({"msg": "Review deleted successfully."}), 200

# Get All Reviews (Published Only)
@review_bp.route("/reviews", methods=["GET"])
def get_reviews():
    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)

    # Retrieve only published reviews with limit and offset for pagination
    reviews = Review.query.filter(Review.published_at.isnot(None)) \
                          .order_by(Review.created_at.desc()) \
                          .limit(limit) \
                          .offset(offset) \
                          .all()

    return review_schema.ReviewSchema().jsonify(reviews), 200

# Get a Specific Review (Published Only)
@review_bp.route("/reviews/<int:review_id>", methods=["GET"])
def get_review(review_id):
    review = Review.query.filter(Review.id == review_id, Review.published_at.isnot(None)).first_or_404()
    return review_schema.jsonify(review), 200
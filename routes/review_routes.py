from flask import Blueprint, flash, redirect, request, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db
from models.review_model import Review

review_bp = Blueprint("review_bp", __name__)


@review_bp.route("/submit_review", methods=["POST"])
@jwt_required()
def submit_review():
    user_id = get_jwt_identity()
    action = request.form.get("action")

    # If the action is not provided or is invalid
    if action not in ["create", "update", "delete"]:
        flash("Invalid action specified.", "error")
        return redirect(url_for("user_bp.profile"))

    # For creating a new review
    if action == "create":
        try:
            # Get form data
            rating = request.form.get("rating")
            comment = request.form.get("comment")

            # Validate rating input
            if not rating or not (1 <= int(rating) <= 5):
                flash("Rating must be between 1 and 5.", "error")
                return redirect(url_for("user_bp.profile"))

            # Optional: Validate comment (e.g., not empty)
            if not comment or len(comment.strip()) == 0:
                flash("Comment cannot be empty.", "error")
                return redirect(url_for("user_bp.profile"))

            # Create new review
            new_review = Review(rating=int(rating), comment=comment, User_id=user_id)

            # Save to database
            db.session.add(new_review)
            db.session.commit()

            flash("Review submitted successfully!", "success")
            return redirect(url_for("user_bp.profile"))

        except Exception as e:
            db.session.rollback()  # Rollback on error
            flash(f"Error submitting review: {e}", "error")
            return redirect(url_for("user_bp.profile"))

    # For updating an existing review
    elif action == "update":
        try:
            # Get form data
            rating = request.form.get("rating")
            comment = request.form.get("comment")
            review_id = request.form.get("review_id")

            # Validate rating input
            if not rating or not (1 <= int(rating) <= 5):
                flash("Rating must be between 1 and 5.", "error")
                return redirect(url_for("user_bp.profile"))

            # Optional: Validate comment (e.g., not empty)
            if not comment or len(comment.strip()) == 0:
                flash("Comment cannot be empty.", "error")
                return redirect(url_for("user_bp.profile"))

            # Find the review to update
            review = Review.query.get(review_id)
            if review is None:
                flash("Review not found.", "error")
                return redirect(url_for("user_bp.profile"))
            if str(review.User_id) != str(user_id):
                flash("You don't have permission to edit it.", "error")
                return redirect(url_for("user_bp.profile"))

            # Update review
            review.rating = int(rating)
            review.comment = comment
            review.published_at = (
                db.func.now()
            )  # Optional: Update the published timestamp

            # Save to database
            db.session.commit()

            flash("Review updated successfully!", "success")
            return redirect(url_for("user_bp.profile"))

        except Exception as e:
            db.session.rollback()  # Rollback on error
            flash(f"Error updating review: {e}", "error")
            return redirect(url_for("user_bp.profile"))

    # For deleting a review
    elif action == "delete":
        try:
            # Get review id from form data
            review_id = request.form.get("review_id")

            review = Review.query.get(review_id)
            if not review:
                flash("Review not found.", "error")
                return redirect(url_for("user_bp.profile"))

            # Proceed with your permission check after finding the review
            if str(review.User_id) != str(user_id):
                flash("You don't have permission to delete this review.", "error")
                return redirect(url_for("user_bp.profile"))

            # Delete review
            db.session.delete(review)
            db.session.commit()

            flash("Review deleted successfully!", "success")
            return redirect(url_for("user_bp.profile"))

        except Exception as e:
            db.session.rollback()  # Rollback on error
            flash(f"Error deleting review: {e}", "error")
            return redirect(url_for("user_bp.profile"))

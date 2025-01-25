from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError
from models.news_model import News
from utils.validator_utils import is_admin
from db import db

MAX_LIMIT = 50

news_bp = Blueprint("news_bp", __name__)

@news_bp.route('/news', methods=['GET'])
def news():
    limit = min(request.args.get("limit", default=5, type=int), MAX_LIMIT)
    offset = max(request.args.get("offset", default=0, type=int), 0)

    # Fetch total count for pagination
    total_news_count = News.query.filter(News.published_at != None).count()

    # Fetch paginated news items
    news_items = (
        News.query.filter(News.published_at != None)
        .order_by(News.published_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    # Calculate pagination data
    current_page = (offset // limit) + 1
    total_pages = (total_news_count + limit - 1) // limit  # Ceiling division for total pages

    return render_template(
        "news.jinja",
        title="News",
        page="news",
        news_items=news_items,
        current_page=current_page,
        total_pages=total_pages,
        limit=limit,
    ), 200

@news_bp.route('/manage_news', methods=['POST'])
@jwt_required()
def manage_news():
    user_id = get_jwt_identity()
    if is_admin():
        return redirect(url_for("home_bp.home"))
    
    action = request.form.get('action')
    news_id = request.form.get('news_id')
    news = News.query.get(news_id) if news_id else None

    if action == "create":
        title = request.form.get('title')
        content = request.form.get('content')
        author_id = user_id  # Set the current admin user as the author

        if not title or not content:
            flash("Title and content are required to create news.", "error")
            return redirect(url_for('admin_bp.admin'))
        
        new_news = News(title=title, content=content, author_id=author_id)
        try:
            db.session.add(new_news)
            db.session.commit()
            flash("News created successfully!", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Error creating news: {str(e)}", "error")
    
    elif action == "edit" and news:
        news.title = request.form.get('title', news.title)
        news.content = request.form.get('content', news.content)

        # Handle the publish checkbox
        if "publish" in request.form:
            news.published_at = datetime.utcnow()  # Set published_at to now if checkbox is checked
        else:
            news.published_at = None  # Clear published_at if checkbox is unchecked

        try:
            db.session.commit()
            flash("News updated successfully!", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Error updating news: {str(e)}", "error")
    
    elif action == "delete" and news:
        try:
            db.session.delete(news)
            db.session.commit()
            flash("News deleted successfully!", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Error deleting news: {str(e)}", "error")
    else:
        flash("Invalid action or news not found.", "error")
    
    return redirect(url_for('admin_bp.admin'))
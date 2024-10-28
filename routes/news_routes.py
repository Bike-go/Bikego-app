from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models.news_model import News
from datetime import datetime
from utils.validator_utils import is_admin_or_employee
from db import db

news_bp = Blueprint("news_bp", __name__)

# Public endpoint to fetch latest news articles with pagination
@news_bp.route("/get-news", methods=["GET"])
def get_latest_news():
    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)

    latest_news = (
        News.query.order_by(News.published_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    news_data = [news.to_dict() for news in latest_news]
    
    return jsonify(news_data), 200

# Private endpoint to create a new news article
@news_bp.route("/create-news", methods=["POST"])
@jwt_required()
def create_news():
    if not is_admin_or_employee():
        return jsonify({"msg": "Admin or Employee access required."}), 403

    data = request.json
    new_news = News(
        title=data['title'],
        content=data['content'],
        created_at=datetime.utcnow(),
        published_at=data['published_at'],
    )
    
    db.session.add(new_news)
    db.session.commit()
    
    return jsonify(new_news.to_dict()), 201

# Private endpoint to update an existing news article
@news_bp.route("/update-news/<int:news_id>", methods=["PUT"])
@jwt_required()
def update_news(news_id):
    if not is_admin_or_employee():
        return jsonify({"msg": "Admin or Employee access required."}), 403

    data = request.json
    news_article = News.query.get(news_id)
    
    if not news_article:
        return jsonify({"msg": "News article not found."}), 404
    
    news_article.title = data.get('title', news_article.title)
    news_article.content = data.get('content', news_article.content)
    news_article.published_at = data.get('published_at', news_article.published_at)
    
    db.session.commit()
    
    return jsonify(news_article.to_dict()), 200

# Private endpoint to delete a news article
@news_bp.route("/delete-news/<int:news_id>", methods=["DELETE"])
@jwt_required()
def delete_news(news_id):
    if not is_admin_or_employee():
        return jsonify({"msg": "Admin or Employee access required."}), 403

    news_article = News.query.get(news_id)
    
    if not news_article:
        return jsonify({"msg": "News article not found."}), 404
    
    db.session.delete(news_article)
    db.session.commit()
    
    return jsonify({"msg": "News article deleted."}), 200
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import DevelopmentConfig, ProductionConfig
from upload_schema import upload_schema
from routes import (bike_bp, category_bp, inspection_bp, maintenance_bp, news_bp, payment_bp, picture_bp, price_bp, rental_bp, repair_bp, reservation_bp, review_bp, statistics_bp, user_bp)
from db import db

app = Flask(__name__)

if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

db.init_app(app)
jwt = JWTManager(app)

@app.before_request
def check_db():
    upload_schema(False)

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong'}), 200

app.register_blueprint(bike_bp, url_prefix='/api/bikes')
app.register_blueprint(category_bp, url_prefix='/api/categories')
app.register_blueprint(inspection_bp, url_prefix='/api/inspections')
app.register_blueprint(maintenance_bp, url_prefix='/api/maintenance')
app.register_blueprint(news_bp, url_prefix='/api/news')
app.register_blueprint(payment_bp, url_prefix='/api/payments')
app.register_blueprint(picture_bp, url_prefix='/api/pictures')
app.register_blueprint(price_bp, url_prefix='/api/prices')
app.register_blueprint(rental_bp, url_prefix='/api/rentals')
app.register_blueprint(repair_bp, url_prefix='/api/repairs')
app.register_blueprint(reservation_bp, url_prefix='/api/reservation')
app.register_blueprint(review_bp, url_prefix='/api/reviews')
app.register_blueprint(statistics_bp, url_prefix='/api/statistics')
app.register_blueprint(user_bp, url_prefix='/api/users')

if __name__ == "__main__":
    app.run()
import os
from flask import Flask, jsonify, redirect, render_template, url_for
from flask_jwt_extended import JWTManager
from config import DevelopmentConfig, ProductionConfig
from upload_schema import upload_schema
from routes import (bike_bp, category_bp, inspection_bp, instance_bike_bp, maintenance_bp, news_bp, payment_bp, picture_bp, price_bp, rental_bp, repair_bp, reservation_bp, review_bp, user_bp)
from db import db

app = Flask(__name__)

if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")

db.init_app(app)
jwt = JWTManager(app)

@app.route('/', methods=['GET'])
def home():
    return render_template('HomePage.html'), 200

@app.errorhandler(404)
def not_found():
    return redirect(url_for('home')), 302

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong'}), 200

app.register_blueprint(bike_bp, url_prefix='/api/bikes')
app.register_blueprint(category_bp, url_prefix='/api/categories')
app.register_blueprint(inspection_bp, url_prefix='/api/inspections')
app.register_blueprint(instance_bike_bp, url_prefix='/api/instance_bike')
app.register_blueprint(maintenance_bp, url_prefix='/api/maintenance')
app.register_blueprint(news_bp, url_prefix='/api/news')
app.register_blueprint(payment_bp, url_prefix='/api/payments')
app.register_blueprint(picture_bp, url_prefix='/api/pictures')
app.register_blueprint(price_bp, url_prefix='/api/prices')
app.register_blueprint(rental_bp, url_prefix='/api/rentals')
app.register_blueprint(repair_bp, url_prefix='/api/repairs')
app.register_blueprint(reservation_bp, url_prefix='/api/reservation')
app.register_blueprint(review_bp, url_prefix='/api/reviews')
app.register_blueprint(user_bp, url_prefix='/api/users')

if __name__ == "__main__":
    try:
        upload_schema(False)
    except Exception as e:
        print("Schema is set up")
    finally:
        app.run(host=HOST, port=PORT)
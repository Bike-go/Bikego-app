from flask import Flask, jsonify, redirect, render_template, url_for, request
from flask_jwt_extended import JWTManager
from flask_wtf import CSRFProtect
from sqlalchemy import create_engine, inspect, text
from config import Config
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate
from db import db
from routes import bike_bp, category_bp, inspection_bp, instance_bike_bp, maintenance_bp, news_bp, payment_bp, picture_bp, price_bp, rental_bp, repair_bp, reservation_bp, review_bp, user_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
app.secret_key = app.config["SECRET_KEY"]
csrf = CSRFProtect(app)
jwt = JWTManager(app)

def check_and_upload_schema(schema_name: str):
    """
    Checks if the database schema exists. If not, it creates it. 
    Also checks if the expected tables are present and creates missing ones.
    """
    with app.app_context():
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        inspector = inspect(engine)
        try:
            with engine.connect() as conn:
                schema_check_query = f"""
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name = :schema_name
                """
                result = conn.execute(text(schema_check_query), {"schema_name": schema_name}).fetchone()
                if not result:
                    print(f"Schema '{schema_name}' does not exist. Creating schema...")
                    conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
                    conn.commit()
                    print(f"Schema '{schema_name}' created successfully.")
                else:
                    print(f"Schema '{schema_name}' already exists.")
            existing_tables = inspector.get_table_names(schema=schema_name)
            model_tables = db.metadata.tables.keys()
            missing_tables = [table for table in model_tables if table not in existing_tables]
            if missing_tables:
                print(f"Missing tables detected in schema '{schema_name}': {missing_tables}")
                print("Creating missing tables...")
                db.create_all()
                print("Schema updated successfully.")
            else:
                print("All tables are present. No changes made to the schema.")
        except SQLAlchemyError as e:
            print(f"Error while inspecting or updating the database: {e}")
        finally:
            engine.dispose()

@app.route('/', methods=['GET'])
def root():
    return redirect(url_for("home")), 301

@app.route('/home', methods=['GET'])
def home():
    return render_template("home.jinja", title="Home", page="home"), 200

@app.route('/news', methods=['GET'])
def news():
    return render_template("news.jinja", title="News", page="news"), 200

@app.route('/rentals', methods=['GET'])
def rentals():
    return render_template("rentals.jinja", title="Rentals", page="rentals"), 200

@app.route('/photos', methods=['GET'])
def photos():
    return render_template("photos.jinja", title="Photos", page="photos"), 200

@app.route('/contacts', methods=['GET'])
def contacts():
    return render_template("contacts.jinja", title="Contacts", page="contacts"), 200

app.register_blueprint(bike_bp, url_prefix='/bikes')
app.register_blueprint(category_bp, url_prefix='/categories')
app.register_blueprint(inspection_bp, url_prefix='/inspections')
app.register_blueprint(instance_bike_bp, url_prefix='/instance_bike')
app.register_blueprint(maintenance_bp, url_prefix='/maintenance')
app.register_blueprint(news_bp, url_prefix='/news')
app.register_blueprint(payment_bp, url_prefix='/payments')
app.register_blueprint(picture_bp, url_prefix='/pictures')
app.register_blueprint(price_bp, url_prefix='/prices')
app.register_blueprint(rental_bp, url_prefix='/rentals')
app.register_blueprint(repair_bp, url_prefix='/repairs')
app.register_blueprint(reservation_bp, url_prefix='/reservation')
app.register_blueprint(review_bp, url_prefix='/reviews')
app.register_blueprint(user_bp, url_prefix='/')

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    user_id = jwt_data.get('sub')
    if user_id:
        # Determine the original URL or a fallback URL
        original_url = request.referrer or url_for('home', _external=True)
        # Redirect to the refresh_token endpoint with `next` parameter
        # Adjust to use `POST` request, ensuring the original URL is passed in the body or as part of the form
        return redirect(url_for('user_bp.refresh_token', next=original_url, _external=True), 307)
    # If no user ID is found in the token, return an error message
    return jsonify({"message": "Token has expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": error}), 401

@jwt.unauthorized_loader
def missing_token_error(error):
    return jsonify({"message": error}), 401

if __name__ == "__main__":
    try:
        check_and_upload_schema(app.config['POSTGRES_SCHEMA'])
    except Exception as e:
        print(f"Error setting up schema: {e}")
    finally:
        app.run(host=app.config['FLASK_HOST'], port=app.config['FLASK_PORT'])
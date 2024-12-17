import os
from flask import Flask, flash, jsonify, redirect, render_template, url_for, request
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from flask_wtf import CSRFProtect
from sqlalchemy import create_engine, inspect, text
from config import Config
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate
from db import db
from models.bike_model import Bike, BrakeTypeEnum, FrameMaterialEnum
from models.instance_bike_model import BikeSizeEnum, BikeStatusEnum, InstanceBike
from models.news_model import News
from routes import bike_bp, category_bp, inspection_bp, instance_bike_bp, maintenance_bp, news_bp, payment_bp, picture_bp, price_bp, rental_bp, repair_bp, reservation_bp, review_bp, user_bp
from utils.email_utils import send_contact_form

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
                    try:
                        data_file = "data.sql"
                        if not os.path.exists(data_file):
                            print(f"Data file '{data_file}' not found. Skipping data insertion.")
                        else:
                            with open(data_file, "r") as f:
                                sql_script = f.read()
                                conn.execute(text(sql_script))
                                conn.commit()
                                print("Data inserted successfully.")
                    except Exception as e:
                        print(f"Error inserting data into schema '{schema_name}': {e}")
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
    news_items = News.query.filter(News.published_at != None).order_by(News.published_at.desc()).all()
    return render_template("news.jinja", title="News", page="news", news_items=news_items), 200

from flask import request

@app.route('/rentals', methods=['GET'])
def rentals():
    # Fetch query parameters for all filters
    brand_filter = request.args.get('brand', None)
    model_filter = request.args.get('model', None)
    frame_material_filter = request.args.get('frame_material', None)
    brake_type_filter = request.args.get('brake_type', None)
    size_filter = request.args.get('size', None)
    color_filter = request.args.get('color', None)
    status_filter = request.args.get('status', None)
    search_query = request.args.get('search', None)

    # Base query to fetch bike instances joined with Bike
    query = InstanceBike.query.join(Bike)

    # Apply filters dynamically
    if brand_filter:
        query = query.filter(Bike.brand == brand_filter)
    if model_filter:
        query = query.filter(Bike.model == model_filter)
    if frame_material_filter:
        query = query.filter(Bike.frame_material == frame_material_filter)
    if brake_type_filter:
        query = query.filter(Bike.brake_type == brake_type_filter)
    if size_filter:
        query = query.filter(InstanceBike.size == size_filter)
    if color_filter:
        query = query.filter(InstanceBike.color.ilike(f"%{color_filter}%"))
    if status_filter:
        query = query.filter(InstanceBike.status == status_filter)
    if search_query:
        query = query.filter(
            (Bike.model.ilike(f"%{search_query}%")) | 
            (Bike.description.ilike(f"%{search_query}%"))
        )

    # Execute the query
    bike_instances = query.all()

    # Fetch distinct options dynamically for dropdowns
    brands = db.session.query(Bike.brand).distinct().all()
    brands = [brand[0] for brand in brands]

    models = db.session.query(Bike.model).distinct().all()
    models = [model[0] for model in models]

    frame_materials = [material.value for material in FrameMaterialEnum]
    brake_types = [brake.value for brake in BrakeTypeEnum]
    sizes = [size.value for size in BikeSizeEnum]
    statuses = [status.value for status in BikeStatusEnum]

    colors = db.session.query(InstanceBike.color).distinct().all()
    colors = [color[0] for color in colors]

    return render_template(
        "rentals.jinja",
        title="Bike Instances",
        bike_instances=bike_instances,
        brands=brands,
        models=models,
        frame_materials=frame_materials,
        brake_types=brake_types,
        sizes=sizes,
        colors=colors,
        statuses=statuses,
        selected_filters={
            "brand": brand_filter,
            "model": model_filter,
            "frame_material": frame_material_filter,
            "brake_type": brake_type_filter,
            "size": size_filter,
            "color": color_filter,
            "status": status_filter,
            "search": search_query,
        },
    ), 200

@app.route('/rentals-detail/<uuid:bike_instance_id>', methods=['GET'])
def rentals_detail(bike_instance_id):
    bike_instance = InstanceBike.query.filter_by(id=bike_instance_id).join(Bike).first()
    if not bike_instance:
        return redirect(url_for("rentals")), 301
    return render_template("bike_detail.jinja", title="Bike Detail", bike_instance=bike_instance), 200

@app.route('/photos', methods=['GET'])
def photos():
    return render_template("photos.jinja", title="Photos", page="photos"), 200

@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        if not name or not email or not message:
            flash("Please fill in all fields.", "error")
            return render_template("contacts.jinja", title="Contacts", page="contacts"), 200
        try:
            send_contact_form(email, name, message)
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            flash(f"Failed to send your message. Please try again later. Error: {e}", "error")
        return render_template("contacts.jinja", title="Contacts", page="contacts"), 200
    return render_template("contacts.jinja", title="Contacts", page="contacts"), 200

@app.route('/tos', methods=['GET'])
def tos():
    return render_template("terms_of_services.jinja", title="Terms of Service", page="tos"), 200

@app.route('/privacy', methods=['GET'])
def privacy():
    return render_template("privacy_policy.jinja", title="Privacy Policy", page="privacy"), 200

@app.route('/cookies', methods=['GET'])
def cookies():
    return render_template("cookies_policy.jinja", title="Cookies Policy", page="cookies"), 200

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
        original_url = request.referrer or url_for('home', _external=True)
        return redirect(url_for('user_bp.refresh_token', next=original_url, _external=True), 307)
    return jsonify({"message": "Token has expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": error}), 401

@jwt.unauthorized_loader
def missing_token_error(error):
    return jsonify({"message": error}), 401

@app.context_processor
def inject_user():
    try:
        verify_jwt_in_request(optional=True)
        is_logged_in = bool(get_jwt_identity())
    except Exception:
        is_logged_in = False
    return {'is_logged_in': is_logged_in}

if __name__ == "__main__":
    try:
        check_and_upload_schema(app.config['POSTGRES_SCHEMA'])
    except Exception as e:
        print(f"Error setting up schema: {e}")
    finally:
        app.run(host=app.config['FLASK_HOST'], port=app.config['FLASK_PORT'])
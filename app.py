from flask import Flask, jsonify, make_response, redirect, render_template, request, session, url_for
from flask_jwt_extended import JWTManager, get_jwt, verify_jwt_in_request
from flask_wtf import CSRFProtect
from sqlalchemy import create_engine, inspect, text
from config import Config
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate
from db import db
from flask_wtf.csrf import generate_csrf
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
    print(jwt_data.get('sub'))
    if jwt_data.get('sub'):
        # Get the current URL or use `request.referrer`
        original_url = request.referrer or url_for('home', _external=True)
        
        # Redirect to the refresh_token route with `next` parameter
        return redirect(
            url_for('user_bp.refresh_token', next=original_url, _external=True),
            307
        )
    return jsonify({"message": "Token has expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "Invalid token" + error}), 401

@jwt.unauthorized_loader
def missing_token_error(error):
    return jsonify({"message": "Missing token" + error}), 401

@app.before_request
def log_csrf_tokens():
    print('-')
    try:
        verify_jwt_in_request()
        print("JWT CSRF token: ", get_jwt().get('csrf'))
    except Exception as e:
        print(e)
    print("Form Data:", request.form.get('csrf_token'))
    print("Cookie Token:", request.cookies.get('csrf_token'))
    print("Session Token:", session.get('csrf_token'))
    print('-')

#@app.before_request
#def set_csrf_cookie():
    # Generate a new CSRF token for each request
#    csrf_token = generate_csrf()
#    session['csrf_token'] = csrf_token  # Store in session
#    response = make_response(jsonify({"message": "CSRF token set"}))
#    response.set_cookie('csrf_token', csrf_token)  # Set token in cooki

#@app.after_request
#def regenerate_csrf_token(response):
#    csrf_token = generate_csrf()
#    session['csrf_token'] = csrf_token
#    response.set_cookie('csrf_token', csrf_token)
#    return response

#@app.before_request
#def set_csrf_cookie():
#    if 'csrf_token' not in session:
#        csrf_token = generate_csrf()  # Generate CSRF token
#        session['csrf_token'] = csrf_token
#        response = make_response()  # Empty response to set cookies
#        response.set_cookie('csrf_token', csrf_token)  # Store CSRF token in cookie
#        return response

if __name__ == "__main__":
    try:
        check_and_upload_schema(app.config['POSTGRES_SCHEMA'])
    except Exception as e:
        print(f"Error setting up schema: {e}")
    finally:
        app.run(host=app.config['FLASK_HOST'], port=app.config['FLASK_PORT'])
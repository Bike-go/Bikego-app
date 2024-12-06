
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_jwt_extended import JWTManager, get_jwt_identity, unset_jwt_cookies
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
app.secret_key = app.config["JWT_SECRET_KEY"]
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
def view_Home():
    return render_template("homePage.jinja", title="Domů"), 200

@app.route('/Novinky')
def view_Novinky():
    return render_template("novinky.jinja", title="Novinky")

@app.route('/Půjčovná')
def view_Pujcovna():
    return render_template("pujcovna.jinja", title="Půjčovná")

@app.route('/Foto')
def view_Foto():
    return render_template("foto.jinja", title="Foto")

@app.route('/Kontakt')
def view_Kontakt():
    return render_template("kontakt.jinja", title="Kontakt")

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

# Handle 401 Unauthorized errors globally
@app.errorhandler(401)
def unauthorized(error):
    return redirect(url_for("user_bp.login"))

# Handle invalid JWT tokens (e.g., malformed, incorrect)
@jwt.invalid_token_loader
def invalid_token_callback(jwt_payload):
    # Redirect to login with a flash message
    flash("Invalid token. Please log in again.", "error")
    return redirect(url_for("user_bp.login"))

# Handle cases where the Authorization header is missing
@jwt.unauthorized_loader
def unauthorized_callback(error):
    # Redirect to login with a flash message
    flash("Missing Authorization Header. Please log in.", "error")
    return redirect(url_for("user_bp.login"))

# Handle expired tokens
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    if jwt_payload['type'] == 'access':
        try:
            # Try to get the user's identity from the refresh token
            current_user = get_jwt_identity()  # Raises an error if refresh token is invalid
            # If valid, redirect to refresh token endpoint
            return redirect(url_for("user_bp.refresh", next=request.path))
        except:
            # Handle invalid or expired refresh token
            flash("Your session has expired. Please log in again.", "error")
            response = jsonify({"msg": "Refresh token has expired or is invalid. Please log in again."})
            unset_jwt_cookies(response)
            return redirect(url_for("user_bp.login"))
    else:
        # Handle refresh token expiration
        flash("Refresh token expired. Please log in again.", "error")
        response = jsonify({"msg": "Refresh token has expired. Please log in again."})
        unset_jwt_cookies(response)
        return redirect(url_for("user_bp.login"))

if __name__ == "__main__":
    try:
        check_and_upload_schema(app.config['POSTGRES_SCHEMA'])
    except Exception as e:
        print(f"Error setting up schema: {e}")
    finally:
        app.run(host=app.config['FLASK_HOST'], port=app.config['FLASK_PORT'])
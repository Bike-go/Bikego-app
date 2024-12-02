import os
from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from sqlalchemy import create_engine, inspect, text
from config import DevelopmentConfig, ProductionConfig
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate
from models import __init__
from db import db
from routes import (bike_bp, category_bp, inspection_bp, instance_bike_bp, maintenance_bp, news_bp, payment_bp, picture_bp, price_bp, rental_bp, repair_bp, reservation_bp, review_bp, user_bp)

app = Flask(__name__)

if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
app.secret_key = app.config['JWT_SECRET_KEY']

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

@app.route('/login')
def view_login():
    return render_template("login.jinja", title="Přihlášení", page="login")

@app.route('/register')
def view_register():
    return render_template("register.jinja", title="Registrace", page="register")

@app.route('/confirm_password')
def view_new_pass():
    return render_template("new_pass.jinja", title="Obnovení hesla", page="confirm_password")

@app.route('/reset_password')
def view_reset_pass():
    return render_template("reset_pass.jinja", title="Obnovení hesla", page="reset_password")

@app.route('/profile')
def view_profile():
    return render_template("profile.jinja", title="Profil")

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
app.register_blueprint(user_bp, url_prefix='/users')

if __name__ == "__main__":
    try:
        check_and_upload_schema(app.config['POSTGRES_SCHEMA'])
    except Exception as e:
        print(f"Error setting up schema: {e}")
    finally:
        app.run(host=app.config['FLASK_HOST'], port=app.config['FLASK_PORT'])
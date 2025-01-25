import os
from flask import Flask, request, redirect, url_for
from flask_jwt_extended import (
    JWTManager,
    get_jwt_identity,
    verify_jwt_in_request,
)
from flask_wtf import CSRFProtect
from sqlalchemy import create_engine, inspect, text
from config import Config
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate
from db import db
from routes import (
    admin_bp,
    contacts_bp,
    home_bp,
    legal_notices_bp,
    news_bp,
    photos_bp,
    rentals_bp,
    servis_bp,
    user_bp,
)

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
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        inspector = inspect(engine)
        try:
            with engine.connect() as conn:
                schema_check_query = f"""
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name = :schema_name
                """
                result = conn.execute(
                    text(schema_check_query), {"schema_name": schema_name}
                ).fetchone()
                if not result:
                    print(f"Schema '{schema_name}' does not exist. Creating schema...")
                    conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
                    conn.commit()
                    print(f"Schema '{schema_name}' created successfully.")
                else:
                    print(f"Schema '{schema_name}' already exists.")

                existing_tables = inspector.get_table_names(schema=schema_name)
                expected_tables = [
                    f"{schema_name}.{table}" for table in existing_tables
                ]
                model_tables = db.metadata.tables.keys()
                missing_tables = [
                    table for table in model_tables if table not in expected_tables
                ]
                if missing_tables:
                    print(
                        f"Missing tables detected in schema '{schema_name}': {missing_tables}"
                    )
                    print("Creating missing tables...")
                    db.create_all()
                    print("Schema updated successfully.")
                    try:
                        data_file = "data.sql"
                        if not os.path.exists(data_file):
                            print(
                                f"Data file '{data_file}' not found. Skipping data insertion."
                            )
                        else:
                            with open(data_file, "r", encoding="utf-8") as f:
                                sql_script = f.read()
                                conn.execute(text(sql_script))
                                conn.commit()
                                print("Data inserted successfully.")
                    except Exception as e:
                        print(f"Error inserting data into schema '{schema_name}': {e}")
                else:
                    print("All tables are present. No changes made to the schema.")
        except SQLAlchemyError as e:
            print(f"Error while inspecting or updating the database: {e}")
        finally:
            engine.dispose()


@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for("home_bp.home")), 301


@app.route("/", methods=["GET"])
def root():
    return redirect(url_for("home_bp.home")), 301


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    user_id = jwt_data.get("sub")
    if user_id:
        original_url = request.referrer or url_for("home_bp.home", _external=True)
        return redirect(
            url_for("user_bp.refresh_token", next=original_url, _external=True), 307
        )
    return redirect(url_for("user_bp.login", next=request.url, _external=True), 307)


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return redirect(url_for("home_bp.home", _external=True), 307)


@jwt.unauthorized_loader
def missing_token_error(error):
    if error.startswith("Missing"):
        return redirect(url_for("user_bp.login", next=request.url, _external=True), 307)
    return redirect(url_for("home_bp.home", _external=True), 307)


@app.context_processor
def inject_user():
    try:
        verify_jwt_in_request(optional=True)
        is_logged_in = bool(get_jwt_identity())
    except Exception:
        is_logged_in = False
    return {"is_logged_in": is_logged_in}


app.register_blueprint(admin_bp, url_prefix="/")
app.register_blueprint(contacts_bp, url_prefix="/")
app.register_blueprint(home_bp, url_prefix="/")
app.register_blueprint(legal_notices_bp, url_prefix="/")
app.register_blueprint(news_bp, url_prefix="/")
app.register_blueprint(photos_bp, url_prefix="/")
app.register_blueprint(rentals_bp, url_prefix="/")
app.register_blueprint(servis_bp, url_prefix="/")
app.register_blueprint(user_bp, url_prefix="/")


if __name__ == "__main__":
    try:
        check_and_upload_schema(app.config["POSTGRES_SCHEMA"])
    except Exception as e:
        print(f"Error setting up schema: {e}")
    finally:
        app.run(host=app.config["FLASK_HOST"], port=app.config["FLASK_PORT"])

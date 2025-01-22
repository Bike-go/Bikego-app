from datetime import datetime
import os
from flask import Flask, request, flash, jsonify, redirect, render_template, url_for
from flask_jwt_extended import JWTManager, get_jwt, get_jwt_identity, jwt_required, verify_jwt_in_request
from flask_wtf import CSRFProtect
from sqlalchemy import create_engine, inspect, text
from config import Config
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate
from db import db
from models.bike_model import Bike, BrakeTypeEnum, FrameMaterialEnum
from models.inspection_model import Inspection
from models.instance_bike_model import BikeSizeEnum, BikeStatusEnum, InstanceBike
from models.news_model import News
from models.price_model import Price
from models.rental_model import Rental
from models.reservation_model import Reservation
from models.review_model import Review
from models.user_model import User, UserRoleEnum
from routes import user_bp
from utils.email_utils import send_contact_form
from flask_wtf.csrf import generate_csrf

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
                else:
                    print("All tables are present. No changes made to the schema.")
        except SQLAlchemyError as e:
            print(f"Error while inspecting or updating the database: {e}")
        finally:
            engine.dispose()

@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for("home")), 301

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

@app.route('/rentals', methods=['GET'])
def rentals():
    brand_filter = request.args.getlist('brand')
    model_filter = request.args.getlist('model')
    frame_material_filter = request.args.getlist('frame_material')
    brake_type_filter = request.args.getlist('brake_type')
    size_filter = request.args.getlist('size')
    color_filter = request.args.getlist('color')
    status_filter = request.args.getlist('status')
    search_query = request.args.get('search', None)
    
    query = InstanceBike.query.join(Bike)
    
    if brand_filter:
        query = query.filter(Bike.brand.in_(brand_filter))
    if model_filter:
        query = query.filter(Bike.model.in_(model_filter))
    if frame_material_filter:
        query = query.filter(Bike.frame_material.in_(frame_material_filter))
    if brake_type_filter:
        query = query.filter(Bike.brake_type.in_(brake_type_filter))
    if size_filter:
        query = query.filter(InstanceBike.size.in_(size_filter))
    if color_filter:
        query = query.filter(InstanceBike.color.in_(color_filter))
    if status_filter:
        query = query.filter(InstanceBike.status.in_(status_filter))
    if search_query:
        query = query.filter(
            (Bike.model.ilike(f"%{search_query}%")) | 
            (Bike.description.ilike(f"%{search_query}%"))
        )
    
    bike_instances = query.all()
    
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

@app.route('/rentals-detail/<uuid:bike_instance_id>', methods=['GET', 'POST'])
@jwt_required(optional=True)
def rentals_detail(bike_instance_id):
    bike_instance = InstanceBike.query.filter_by(id=bike_instance_id).join(Bike).first()

    if not bike_instance:
        return redirect(url_for("rentals")), 301
    
    if request.method == 'POST':
        try:
            reservation_start = request.form.get("reservation_start")
            reservation_end = request.form.get("reservation_end")
            ready_to_pickup = request.form.get("ready_to_pickup") == "on" 

            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            reservation_start = datetime.strptime(reservation_start, "%Y-%m-%d %H:%M")
            reservation_end = datetime.strptime(reservation_end, "%Y-%m-%d %H:%M")
            
            new_reservation = Reservation(
                reservation_start=reservation_start,
                reservation_end=reservation_end,
                ready_to_pickup=ready_to_pickup,
                User_id=user_id,
                Instance_Bike_id=bike_instance.id
            )
            
            db.session.add(new_reservation)
            db.session.commit()

            flash("Reservation created successfully!", "success")

            try:
                csrf_token = get_jwt()["csrf"]
            except Exception as e:
                csrf_token = generate_csrf()
            
            return redirect(url_for("rentals_detail", bike_instance_id=bike_instance.id, csrf_token=csrf_token)), 301

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating reservation: {e}", "error")

    try:
        csrf_token = get_jwt()["csrf"]
    except Exception as e:
        csrf_token = generate_csrf()
    
    return render_template("bike_detail.jinja", title="Bike Detail", bike_instance=bike_instance, csrf_token=csrf_token), 200

@app.route("/submit-review/<uuid:bike_instance_id>", methods=["POST"])
@jwt_required()
def submit_review(bike_instance_id):
    user_id = get_jwt_identity()
    
    bike_instance = InstanceBike.query.get(bike_instance_id)

    if not bike_instance:
        flash("Bike instance not found.", "error")
        return redirect(url_for("rentals"))

    try:
        
        rating = request.form.get("rating")
        comment = request.form.get("comment")
        
        if not rating or not (1 <= int(rating) <= 5):
            flash("Rating must be between 1 and 5.", "error")
            return redirect(url_for("rentals_detail", bike_instance_id=bike_instance_id))
        
        new_review = Review(
            rating=int(rating),
            comment=comment,
            created_at=datetime.utcnow(),
            User_id=user_id
        )
        
        db.session.add(new_review)
        db.session.commit()

        flash("Review submitted successfully!", "success")
        return redirect(url_for("rentals_detail", bike_instance_id=bike_instance_id))

    except Exception as e:
        db.session.rollback()
        flash(f"Error submitting review: {e}", "error")
        return redirect(url_for("rentals_detail", bike_instance_id=bike_instance_id))

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

@app.route('/admin', methods=['GET'])
@jwt_required()
def admin():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role.value not in ['Admin']:
        return redirect(url_for("home"))
    
    users = User.query.order_by(User.created_at.desc()).all()
    news_items = News.query.order_by(News.created_at.desc()).all()
    bikes = InstanceBike.query.all()
    
    try:
        csrf_token = get_jwt()["csrf"]
    except Exception as e:
        csrf_token = generate_csrf()
    
    return render_template(
        "admin_page.jinja",
        title="Admin",
        page="admin",
        users=users,
        news_items=news_items,
        bikes=bikes,
        csrf_token=csrf_token
    ), 200

@app.route('/manage_users', methods=['POST'])
@jwt_required()
def manage_users():
    user_id = get_jwt_identity()
    admin_user = User.query.get(user_id)
    if not admin_user or admin_user.role.value not in ['Admin']:
        return redirect(url_for("home"))
    
    action = request.form.get('action')
    user_id = request.form.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('admin'))
    
    if action == "edit":
        user.username = request.form.get('username', user.username)
        user.email = request.form.get('email', user.email)
        user.phone_number = request.form.get('phone_number', user.phone_number)
        role = request.form.get('role', user.role)
        if role in UserRoleEnum.__members__:
            user.role = UserRoleEnum[role]
        
        try:
            db.session.commit()
            flash("User updated successfully!", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Error updating user: {str(e)}", "error")
    
    elif action == "delete":
        try:
            db.session.delete(user)
            db.session.commit()
            flash("User deleted successfully!", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Error deleting user: {str(e)}", "error")
    
    return redirect(url_for('admin'))

@app.route('/manage_news', methods=['POST'])
@jwt_required()
def manage_news():
    user_id = get_jwt_identity()
    admin_user = User.query.get(user_id)
    if not admin_user or admin_user.role.value not in ['Admin']:
        return redirect(url_for("home"))
    
    action = request.form.get('action')
    news_id = request.form.get('news_id')
    news = News.query.get(news_id) if news_id else None

    if action == "create":
        title = request.form.get('title')
        content = request.form.get('content')
        author_id = user_id  # Set the current admin user as the author

        if not title or not content:
            flash("Title and content are required to create news.", "error")
            return redirect(url_for('admin'))
        
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
    
    return redirect(url_for('admin'))

@app.route('/manage_bikes', methods=['GET', 'POST'])
@jwt_required()
def manage_bikes():
    user_id = get_jwt_identity()
    admin_user = User.query.get(user_id)
    if not admin_user or admin_user.role.value != 'Admin':
        return redirect(url_for("home"))
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            # Create a new bike
            model = request.form.get('model')
            frame_material = request.form.get('frame_material')
            brake_type = request.form.get('brake_type')
            brand = request.form.get('brand')
            description = request.form.get('description')
            category_id = request.form.get('category_id')
            price_id = request.form.get('price_id')
            
            new_bike = Bike(
                model=model,
                frame_material=FrameMaterialEnum[frame_material],
                brake_type=BrakeTypeEnum[brake_type],
                brand=brand,
                description=description,
                Category_id=category_id,
                Price_id=price_id
            )
            db.session.add(new_bike)
            db.session.commit()
            flash("Bike created successfully!", "success")

        elif action == 'edit':
            bike_id = request.form.get('bike_id')
            bike = Bike.query.get(bike_id)
            if bike:
                bike.model = request.form.get('model', bike.model)
                bike.frame_material = FrameMaterialEnum[request.form.get('frame_material', bike.frame_material.name)]
                bike.brake_type = BrakeTypeEnum[request.form.get('brake_type', bike.brake_type.name)]
                bike.brand = request.form.get('brand', bike.brand)
                bike.description = request.form.get('description', bike.description)
                bike.Category_id = request.form.get('category_id', bike.Category_id)
                bike.Price_id = request.form.get('price_id', bike.Price_id)

                db.session.commit()
                flash("Bike updated successfully!", "success")
            else:
                flash("Bike not found.", "error")
        
        elif action == 'delete':
            bike_id = request.form.get('bike_id')
            bike = Bike.query.get(bike_id)
            if bike:
                db.session.delete(bike)
                db.session.commit()
                flash("Bike deleted successfully!", "success")
            else:
                flash("Bike not found.", "error")

        return redirect(url_for('manage_bikes'))

    # Fetch bikes to display in template
    bikes = Bike.query.all()
    return render_template('manage_bikes.html', bikes=bikes)

@app.route('/manage_instance_bikes', methods=['GET', 'POST'])
@jwt_required()
def manage_instance_bikes():
    user_id = get_jwt_identity()
    admin_user = User.query.get(user_id)
    if not admin_user or admin_user.role.value != 'Admin':
        return redirect(url_for("home"))

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            bike_id = request.form.get('bike_id')
            size = request.form.get('size')
            color = request.form.get('color')
            new_instance = InstanceBike(
                size=BikeSizeEnum[size],
                color=color,
                Bike_id=bike_id
            )
            db.session.add(new_instance)
            db.session.commit()
            flash("Instance created successfully!", "success")

        elif action == 'edit':
            instance_id = request.form.get('instance_id')
            instance = InstanceBike.query.get(instance_id)
            if instance:
                instance.size = request.form.get('size', instance.size)
                instance.color = request.form.get('color', instance.color)

                db.session.commit()
                flash("Instance updated successfully!", "success")
            else:
                flash("Instance not found.", "error")

        elif action == 'delete':
            instance_id = request.form.get('instance_id')
            instance = InstanceBike.query.get(instance_id)
            if instance:
                db.session.delete(instance)
                db.session.commit()
                flash("Instance deleted successfully!", "success")
            else:
                flash("Instance not found.", "error")

        return redirect(url_for('manage_instance_bikes'))

    # Fetch instance bikes to display in template
    instance_bikes = InstanceBike.query.all()
    return render_template('manage_instance_bikes.html', instance_bikes=instance_bikes)

@app.route('/rental', methods=['GET', 'POST'])
@jwt_required()
def rent_checkout():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role.value not in ['Admin', 'Employee']:
        return redirect(url_for("home"))
    
    csrf_token_from_jwt = get_jwt().get("csrf")

    if request.method == 'GET':
        reservations = Reservation.query.filter_by(ready_to_pickup=True).all()
        
        rentals_to_update = Rental.query.filter(Rental.end_time == Rental.start_time).all()

        return render_template("rent_back_bike.jinja", 
                               title="Reservations for Rental", 
                               reservations=reservations, 
                               rentals_to_update=rentals_to_update,
                               csrf_token=csrf_token_from_jwt), 200
    
    if request.method == 'POST' and 'reservation_id' in request.form:
        reservation_id = request.form.get('reservation_id')
        reservation = Reservation.query.get(reservation_id)

        if not reservation or not reservation.ready_to_pickup:
            flash("Reservation not found or not ready for pickup.", "error")
            return redirect(url_for('rent_checkout'))
        
        rental = Rental(
            User_id=reservation.User_id,
            Instance_Bike_id=reservation.Instance_Bike_id,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),  
            total_price=0  
        )

        try:
            db.session.add(rental)
            instance_bike = InstanceBike.query.get(reservation.Instance_Bike_id)
            instance_bike.status = BikeStatusEnum.Rented
            db.session.commit()
            flash("Rental successfully created!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating rental: {str(e)}", "error")
        
        return redirect(url_for('rent_checkout'))
    
    if request.method == 'POST' and 'rental_id' in request.form:
        rental_id = request.form.get('rental_id')
        end_time = request.form.get('end_time')
        comments = request.form.get('comments')  
        rental = Rental.query.get(rental_id)

        if not rental:
            flash("Rental not found.", "error")
            return redirect(url_for('rent_checkout'))
        
        try:
            end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            flash("Invalid date format for end_time. Use YYYY-MM-DD HH:MM:SS.", "error")
            return redirect(url_for('rent_checkout'))
        
        duration = (end_time - rental.start_time).total_seconds() / 3600

        price = Price.query.first()  

        if not price:
            flash("Price not found.", "error")
            return redirect(url_for('rent_checkout'))

        if duration < 24:
            total_price = round(duration * price.price_per_hour)
        else:
            total_price = round((duration / 24) * price.price_per_day)

        rental.end_time = end_time
        rental.total_price = total_price

        try:
            if comments:
                inspection = Inspection(
                    rental_id=rental.id,
                    User_id=rental.User_id,
                    comments=comments
                )
                db.session.add(inspection)
            
            db.session.commit()
            flash("Rental updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating rental or creating inspection: {str(e)}", "error")

        return redirect(url_for('rent_checkout'))

@app.route('/servis', methods=['GET', 'POST'])
@jwt_required()
def servis():
    user_id = get_jwt_identity()

    user = User.query.get(user_id)
    
    if not user or user.role.value not in ['Admin', 'Service']:
        return redirect(url_for("home"))
    
    csrf_token_from_jwt = get_jwt().get("csrf")

    if request.method == 'POST':
        inspection_id = request.form.get('inspection_id')
        new_status = request.form.get('status')

        inspection = Inspection.query.get(inspection_id)
        if not inspection:
            flash("Inspection not found.", "error")
            return redirect(url_for("servis"))

        instance_bike = (
            InstanceBike.query
            .join(Rental, Rental.Instance_Bike_id == InstanceBike.id)
            .filter(Rental.id == inspection.Rental_id)
            .first()
        )

        if not instance_bike:
            flash("Associated bike not found.", "error")
            return redirect(url_for("servis"))

        valid_statuses = [status.value for status in BikeStatusEnum]
        if new_status not in valid_statuses:
            flash("Invalid status value.", "error")
            return redirect(url_for("servis"))

        try:
            instance_bike.status = new_status
            db.session.commit()
            flash("Bike status updated successfully.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating bike status: {e}", "error")

        return redirect(url_for("servis"))

    inspections = (
        Inspection.query
        .join(Rental, Rental.id == Inspection.Rental_id)
        .join(InstanceBike, Rental.Instance_Bike_id == InstanceBike.id)
        .order_by(Inspection.inspection_date.desc())
        .all()
    )

    valid_statuses = [status.value for status in BikeStatusEnum]
    
    return render_template("servis.jinja", title="Servis", page="servis", inspections=inspections, statuses=valid_statuses, csrf_token=csrf_token_from_jwt), 200

@app.route('/tos', methods=['GET'])
def tos():
    return render_template("terms_of_services.jinja", title="Terms of Service", page="tos"), 200

@app.route('/privacy', methods=['GET'])
def privacy():
    return render_template("privacy_policy.jinja", title="Privacy Policy", page="privacy"), 200

@app.route('/cookies', methods=['GET'])
def cookies():
    return render_template("cookies_policy.jinja", title="Cookies Policy", page="cookies"), 200

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
    if (error.startswith("Missing")):
        return redirect(url_for('user_bp.login', next=request.url, _external=True), 307)
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
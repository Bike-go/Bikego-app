from .admin_routes import admin_bp
from .contacts_routes import contacts_bp
from .home_routes import home_bp
from .instance_bike_routes import instance_bike_bp
from .legal_notices_routes import legal_notices_bp
from .news_routes import news_bp
from .photos_routes import photos_bp
from .rentals_routes import rentals_bp
from .review_routes import review_bp
from .servis_routes import servis_bp
from .user_routes import user_bp

__all__ = [
    'admin_bp', 'contacts_bp', 'home_bp', 'instance_bike_bp', 'legal_notices_bp', 'news_bp', 'photos_bp', 'rentals_bp', 'review_bp', 'servis_bp', 'user_bp'
]
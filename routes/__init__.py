from .bike_routes import bike_bp
from .category_routes import category_bp
from .inspection_routes import inspection_bp
from .instance_bike_routes import instance_bike_bp
from .maintenance_routes import maintenance_bp
from .news_routes import news_bp
from .payment_routes import payment_bp
from .picture_routes import picture_bp
from .price_routes import price_bp
from .rental_routes import rental_bp
from .repair_routes import repair_bp
from .reservation_routes import reservation_bp
from .review_routes import review_bp
from .user_routes import user_bp

__all__ = [
    'bike_bp', 'category_bp', 'inspection_bp', 'instance_bike_bp', 'maintenance_bp', 'news_bp', 'payment_bp', 'picture_bp', 'price_bp', 'rental_bp', 'repair_bp', 'reservation_bp', 'review_bp', 'user_bp'
]
from .trip_routes import trips_bp
from .user_routes import users_bp
from .trip_guest_routes import trip_guests_bp
from .user_upload_routes import user_uploads_bp
from .expenses_routes import expenses_bp
from .location_routes import trip_locations_bp

def register_blueprints(app):
    app.logger.info("Registering blueprints...")
    app.register_blueprint(trips_bp, url_prefix='/trips')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(trip_guests_bp, url_prefix='/trip_guests')
    app.register_blueprint(user_uploads_bp, url_prefix='/user_uploads')
    app.register_blueprint(expenses_bp, url_prefix='/expenses')
    app.register_blueprint(trip_locations_bp, url_prefix='/trip_locations')
    app.logger.info("Blueprints registered successfully.")

from my_app.routes.trip_routes import trips_bp
from my_app.routes.user_routes import users_bp
from my_app.routes.trip_guest_routes import trip_guests_bp
from my_app.routes.user_upload_routes import user_uploads_bp

def register_blueprints(app):
    app.register_blueprint(trips_bp, url_prefix='/trips')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(trip_guests_bp, url_prefix='/trip_guests')
    app.register_blueprint(user_uploads_bp, url_prefix='/user_uploads')

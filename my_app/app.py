from flask import Flask
from my_app.config import get_config
from my_app.models import db
from my_app.routes import register_blueprints
from my_app.logger import setup_logger
from flask_cors import CORS
from my_app.routes.user_routes import init_jwt

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['JWT_SECRET_KEY'] = 'jwt_secret_key'

    app.config.from_object(get_config())

    
    app.logger = setup_logger()

    db.init_app(app)

    init_jwt(app)
    register_blueprints(app)

    with app.app_context():
        try:
            db.create_all()  # Ensure all tables are created
        except Exception as e:
            app.logger.error("Error creating database tables: %s", e)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()

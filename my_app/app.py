import logging
from flask import Flask
from config import get_config
from models import db
from routes import register_blueprints
from firebase_admin import credentials, initialize_app
import boto3
import json

def setup_logging(app):
    log_level = app.config["LOG_LEVEL"]
    log_file = app.config["LOG_FILE"]

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    console_handler.setFormatter(console_format)

    # File Handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_format = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    file_handler.setFormatter(file_format)

    # Add handlers to the Flask app logger
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)

def get_parameter(parameter_name):
    ssm = boto3.client('ssm', region_name='us-east-1')
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
    return response['Parameter']['Value']

def create_app():
    app = Flask(__name__)

    app.config.from_object(get_config())
    
    setup_logging(app)

    firebase_key = get_parameter('firebaseKey')
    firebase_key_dict = json.loads(firebase_key)

    cred = credentials.Certificate(firebase_key_dict)
    initialize_app(cred)

    db.init_app(app)

    register_blueprints(app)

    # TODO: Figure out how to make CORS work globally
    #CORS(app, resources={r"/*": {"origins": "*"}})

    with app.app_context():
        try:
            app.logger.info("Creating database tables")
            db.create_all()  # Ensure all tables are created
            app.logger.info("Database tables created")
        except Exception as e:
            app.logger.error("Error creating database tables: %s", e)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])

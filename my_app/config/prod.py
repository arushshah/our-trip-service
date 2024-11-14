import os
import logging

class ProdConfig:
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL')
    PORT=5555
    HOST="0.0.0.0"
    LOG_LEVEL = logging.WARNING
    LOG_FILE = "app.log"
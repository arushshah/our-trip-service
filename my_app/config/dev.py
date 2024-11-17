import logging

class DevConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    HOST = "localhost"
    PORT = 5555
    LOG_LEVEL = logging.DEBUG
    LOG_FILE = "app.log"
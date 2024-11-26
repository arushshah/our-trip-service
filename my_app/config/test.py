import logging

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///memory'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False  # Often disabled for easier testing
    DEBUG = True
    LOG_LEVEL = logging.DEBUG
    LOG_FILE = "test_app.log"
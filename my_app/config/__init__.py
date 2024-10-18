import os
from my_app.config.dev import DevConfig
from my_app.config.test import TestConfig
from my_app.config.prod import ProdConfig

def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'development':
        return DevConfig
    elif env == 'testing':
        return TestConfig
    elif env == 'production':
        return ProdConfig

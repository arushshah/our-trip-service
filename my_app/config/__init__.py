import os
from config.dev import DevConfig
from config.test import TestConfig
from config.prod import ProdConfig

def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'development':
        return DevConfig
    elif env == 'testing':
        return TestConfig
    elif env == 'production':
        return ProdConfig

import pytest
from app import create_app
from models import db
import os

@pytest.fixture
def app():

    os.environ["FLASK_ENV"] = "testing"
    app = create_app()
    
    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def app_context(app):
    """Automatically pushes an app context for tests."""
    with app.app_context():
        yield

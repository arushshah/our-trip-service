from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from my_app.models.user import User
from my_app.models.trip import Trip
from my_app.models.trip_guest import TripGuest, RsvpStatus
from my_app.models.user_upload import UserUpload
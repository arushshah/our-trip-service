from datetime import datetime
from unittest.mock import patch
from models import User, Trip, db, TripGuest, LocationCategory, TripLocation, TripExpense, TripExpenseShare

def create_user():
    user = User(
        id="test_user",
        phone_number="+11234567890",
        first_name="Test",
        last_name="User"
    )
    db.session.add(user)
    db.session.commit()

def create_trip():
    trip = Trip(
        name="Test Trip",
        description="Test Description",
        token="123",
        host_id="test_user",
        start_date=datetime(2022, 1, 1),
        end_date=datetime(2022, 1, 30)
    )
    db.session.add(trip)
    db.session.commit()

def add_user_to_trip():
    trip_guest = TripGuest(trip_id=1, guest_id="test_user", is_host=True, rsvp_status="YES")
    db.session.add(trip_guest)
    db.session.commit()

# TODO: add tests cases here and need to mock s3 boto client
""" @patch("firebase_admin.auth.verify_id_token")
def test_generate_presigned_url(mock_verify_id_token, client, app_context):
    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }
    create_user()
    create_trip()
    add_user_to_trip()
    response = client.post("/user_uploads/generate-presigned-url",
        json={
            "trip_id": 1,
            "document_category": "travel",
            "file_name": "test_file.txt",
            "file_type": "text/plain",
            "url_type": "upload"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    assert "url" in response.json """

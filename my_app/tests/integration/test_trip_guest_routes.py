from datetime import datetime
from unittest.mock import patch
from models import User, Trip, db, TripGuest

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
    user = User.query.filter_by(id="test_user").first()
    trip = Trip.query.filter_by(id=1).first()
    trip_guest = TripGuest(trip_id=1, guest_id="test_user", is_host=True, rsvp_status="YES")
    db.session.add(trip_guest)
    db.session.commit()

@patch("firebase_admin.auth.verify_id_token")
def test_get_trip_guests(mock_verify_id_token, client, app_context):

    create_user()
    create_trip()
    add_user_to_trip()

    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }
    response = client.get("/trip_guests/get-trip-guests?trip_id=1", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json == {
        'guests': [{'guest_first_name': 'Test', 'guest_last_name': 'User', 'guest_username': 'test_user', 'is_host': True, 'rsvp_status': 'YES'}]
    }

@patch("firebase_admin.auth.verify_id_token")
def test_delete_trip_guest(mock_verify_id_token, client, app_context):

    create_user()
    create_trip()
    add_user_to_trip()

    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }
    response = client.delete("/trip_guests/delete-trip-guest", json={"trip_id": 1, "to_delete_username": "test_user"}, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json == {'message': 'Guest deleted successfully.'}

    trip_guest = TripGuest.query.filter_by(trip_id=1, guest_id="test_user").first()
    assert trip_guest is None

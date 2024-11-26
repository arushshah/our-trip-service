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
def test_create_trip(mock_verify_id_token, client, app_context):

    create_user()
    
    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }
    response = client.post("/trips/create-trip", json={
        "trip_name": "Test Trip",
        "trip_description": "Test Description",
        "trip_start_date": "01/01/2022",
        "trip_end_date": "01/30/2022",
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 201
    assert response.json == {'message': 'Trip created successfully.'}

    trip = Trip.query.filter_by(id=1).first()
    assert trip.name == "Test Trip"
    assert trip.description == "Test Description"
    assert trip.start_date == datetime(2022, 1, 1)
    assert trip.end_date == datetime(2022, 1, 30)
    assert trip.host_id == "test_user"

@patch("firebase_admin.auth.verify_id_token")
def test_create_trip_missing_fields(mock_verify_id_token, client, app_context):

    create_user()
    
    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }
    response = client.post("/trips/create-trip", json={
        "trip_name": "Test Trip",
        "trip_description": "Test Destination",
        "trip_start_date": "01/01/2022",
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 400
    assert response.json == {"error": "Start and end dates are required."}

@patch("firebase_admin.auth.verify_id_token")
def test_create_trip_invalid_dates(mock_verify_id_token, client, app_context):

    create_user()
    
    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }
    response = client.post("/trips/create-trip", json={
        "trip_name": "Test Trip",
        "trip_description": "Test Destination",
        "trip_start_date": "01/01/2022",
        "trip_end_date": "01/01/2021",
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 400
    assert response.json == {"error": "Start date cannot be later than end date."}

@patch("firebase_admin.auth.verify_id_token")
def test_get_trip(mock_verify_id_token, client, app_context):

    create_user()
    create_trip()

    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }
    response = client.get("/trips/get-trip?trip_id=1", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json == {
        'trip_details': {
            'trip_description': 'Test Description', 
            'trip_end_date': '01/30/2022', 
            'trip_hostname': 'test_user', 
            'trip_id': 1, 
            'trip_name': 'Test Trip', 
            'trip_start_date': '01/01/2022', 
            'trip_token': '123'
         }
    }

@patch("firebase_admin.auth.verify_id_token")
def test_get_trip_not_found(mock_verify_id_token, client, app_context):

    create_user()

    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }
    response = client.get("/trips/get-trip?trip_id=1", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 404
    assert response.json == {"error": "Trip not found."}

@patch("firebase_admin.auth.verify_id_token")
def test_update_trip(mock_verify_id_token, client, app_context):

    create_user()
    create_trip()

    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }
    response = client.put("/trips/update-trip", json={
        "trip_id": 1,
        "trip_name": "Updated Trip",
        "trip_description": "Updated Description",
        "trip_start_date": "01/01/2023",
        "trip_end_date": "01/30/2023",
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json == {'message': 'Trip updated successfully.'}

    trip = Trip.query.filter_by(id=1).first()
    assert trip.name == "Updated Trip"
    assert trip.description == "Updated Description"
    assert trip.start_date == datetime(2023, 1, 1)
    assert trip.end_date == datetime(2023, 1, 30)

@patch("firebase_admin.auth.verify_id_token")
def test_delete_trip(mock_verify_id_token, client, app_context):

    create_user()
    create_trip()

    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }
    response = client.delete("/trips/delete-trip", json={"trip_id": 1}, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json == {'message': 'Trip deleted successfully.'}

    trip = Trip.query.filter_by(id=1).first()
    assert trip is None

@patch("firebase_admin.auth.verify_id_token")
def test_get_user_trips(mock_verify_id_token, client, app_context):

    create_user()
    create_trip()
    add_user_to_trip()

    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }
    response = client.get("/trips/get-user-trips", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json == {"trips": [{'rsvp_status': 'YES', 'trip_description': 'Test Description', 'trip_end_date': '01/30/2022', 'trip_hostname': 'test_user', 'trip_id': 1, 'trip_name': 'Test Trip', 'trip_start_date': '01/01/2022', 'trip_token': '123'}]}
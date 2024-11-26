from datetime import datetime
from unittest.mock import patch
from models import User, Trip, db, TripGuest, LocationCategory, TripLocation

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

@patch("firebase_admin.auth.verify_id_token")
def test_add_category(mock_verify_id_token, client, app_context):
    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }

    create_user()
    create_trip()
    add_user_to_trip()

    response = client.post("/trip_locations/add-category", json={"category": "Test Category", "trip_id": 1}, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 201
    assert response.json == {"message": "Category successfully added."}

    category = LocationCategory.query.filter_by(trip_id=1, name="Test Category").first()
    assert category.name == "Test Category"
    assert category.trip_id == 1

    db.session.delete(category)
    db.session.commit()

@patch("firebase_admin.auth.verify_id_token")
def test_delete_category(mock_verify_id_token, client, app_context):
    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }

    create_user()
    create_trip()
    add_user_to_trip()

    category = LocationCategory(trip_id=1, name="Test Category")
    db.session.add(category)
    db.session.commit()

    response = client.delete("/trip_locations/delete-category", json={"category_name": "Test Category", "trip_id": 1}, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json == {"message": "Category successfully deleted."}

    category = LocationCategory.query.filter_by(trip_id=1, name="Test Category").first()
    assert category is None

@patch("firebase_admin.auth.verify_id_token")
def test_update_category(mock_verify_id_token, client, app_context):
    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }

    create_user()
    create_trip()
    add_user_to_trip()

    category = LocationCategory(trip_id=1, name="Test Category")
    db.session.add(category)
    db.session.commit()

    response = client.put("/trip_locations/update-category", json={"old_category_name": "Test Category", "new_category_name": "New Category", "trip_id": 1}, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json == {"message": "Category successfully updated."}

    category = LocationCategory.query.filter_by(trip_id=1, name="New Category").first()
    assert category.name == "New Category"

    db.session.delete(category)
    db.session.commit()

@patch("firebase_admin.auth.verify_id_token")
def test_add_location(mock_verify_id_token, client, app_context):
    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }

    create_user()
    create_trip()
    add_user_to_trip()

    category = LocationCategory(trip_id=1, name="Test Category")
    db.session.add(category)
    db.session.commit()

    response = client.post("/trip_locations/add-location", json={"category_name": "Test Category", "trip_id": 1, "place_name": "Test Location", "lat": 1.0, "lng": 1.0, "place_id": '123"'}, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 201
    assert response.json == {"message": "Location successfully added."}

    location = TripLocation.query.filter_by(trip_id=1, name="Test Location").first()
    assert location.name == "Test Location"
    assert location.trip_id == 1
    assert location.category_id == 1
    assert location.latitude == 1.0
    assert location.longitude == 1.0
    assert location.place_id == '123"'
    assert location.user_id == "test_user"

    db.session.delete(location)
    db.session.delete(category)
    db.session.commit()

@patch("firebase_admin.auth.verify_id_token")
def test_get_locations(mock_verify_id_token, client, app_context):
    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }

    create_user()
    create_trip()
    add_user_to_trip()

    category = LocationCategory(trip_id=1, name="Test Category")
    db.session.add(category)
    db.session.commit()

    location = TripLocation(trip_id=1, name="Test Location", place_id='123', latitude=1.0, longitude=1.0, user_id="test_user", category_id=1)
    db.session.add(location)
    db.session.commit()

    response = client.get("/trip_locations/get-locations?trip_id=1", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json == {"locations": [{'category': 'Test Category', 'category_id': 1, 'lat': 1.0, 'lng': 1.0, 'name': 'Test Location', 'place_id': '123'}]}

    db.session.delete(location)
    db.session.delete(category)
    db.session.commit()

@patch("firebase_admin.auth.verify_id_token")
def test_delete_location(mock_verify_id_token, client, app_context):
    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }

    create_user()
    create_trip()
    add_user_to_trip()

    category = LocationCategory(trip_id=1, name="Test Category")
    db.session.add(category)
    db.session.commit()

    location = TripLocation(trip_id=1, name="Test Location", place_id='123', latitude=1.0, longitude=1.0, user_id="test_user", category_id=1)
    db.session.add(location)
    db.session.commit()

    response = client.delete("/trip_locations/delete-location", json={"place_id": "123", "trip_id": 1}, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json == {"message": "Location successfully deleted."}

    location = TripLocation.query.filter_by(trip_id=1, place_id="123").first()
    assert location is None

    db.session.delete(category)
    db.session.commit()

@patch("firebase_admin.auth.verify_id_token")
def test_update_location(mock_verify_id_token, client, app_context):
    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }

    create_user()
    create_trip()
    add_user_to_trip()

    category = LocationCategory(trip_id=1, name="Test Category")
    category2 = LocationCategory(trip_id=1, name="Test Category 2")

    db.session.add(category)
    db.session.add(category2)
    db.session.commit()

    location = TripLocation(trip_id=1, name="Test Location", place_id='123', latitude=1.0, longitude=1.0, user_id="test_user", category_id=1)
    db.session.add(location)
    db.session.commit()

    response = client.put("/trip_locations/update-location", json={"place_id": "123", "place_name": "New Location", "trip_id": 1, "category_name": "Test Category 2"}, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json == {"message": "Location successfully updated."}

    location = TripLocation.query.filter_by(trip_id=1, name="New Location").first()
    assert location.name == "New Location"
    assert location.category_id == 2

    db.session.delete(location)
    db.session.delete(category)
    db.session.commit()
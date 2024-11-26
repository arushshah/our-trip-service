from datetime import datetime
from unittest.mock import patch
from models import User, Trip, db, TripGuest, LocationCategory, TripLocation, ItineraryEntry

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

def add_item_to_itinerary():
    itinerary_item = ItineraryEntry(
        id="123",
        trip_id=1,
        date=datetime(2024, 11, 8),
        description="Test Description"
    )
    db.session.add(itinerary_item)
    db.session.commit()

@patch("firebase_admin.auth.verify_id_token")
def test_add_item(mock_verify_id_token, client, app_context):
    create_user()
    create_trip()
    add_user_to_trip()

    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }

    response = client.post("/trip_itinerary/add-item", json={
        "trip_id": 1,
        "date": "Fri, 08 Nov 2024 00:00:00 GMT",
        "description": "Test Description",
        "item_id": "123"
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 201
    assert response.json == {"message": "Itinerary item added successfully."}

    itinerary_item = ItineraryEntry.query.filter_by(id="123").first()
    assert itinerary_item.trip_id == 1
    assert itinerary_item.date == datetime(2024, 11, 8)
    assert itinerary_item.description == "Test Description"
    assert itinerary_item.id == "123"

@patch("firebase_admin.auth.verify_id_token")
def test_update_item(mock_verify_id_token, client, app_context):
    create_user()
    create_trip()
    add_user_to_trip()
    add_item_to_itinerary()


    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }

    response = client.put("/trip_itinerary/update-item", json={
        "trip_id": 1,
        "date": "Fri, 08 Nov 2024 00:00:00 GMT",
        "description": "New Test Description",
        "item_id": "123"
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json == {"message": "Itinerary item updated successfully."}

    itinerary_item = ItineraryEntry.query.filter_by(id="123").first()
    assert itinerary_item.trip_id == 1
    assert itinerary_item.date == datetime(2024, 11, 8)
    assert itinerary_item.description == "New Test Description"
    assert itinerary_item.id == "123"
    
@patch("firebase_admin.auth.verify_id_token")
def test_get_itinerary(mock_verify_id_token, client, app_context):
    create_user()
    create_trip()
    add_user_to_trip()
    add_item_to_itinerary()

    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }

    response = client.get("/trip_itinerary/get-itinerary?trip_id=1", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json == {
        'itinerary': [{'date': 'Fri, 08 Nov 2024 00:00:00 GMT', 'description': 'Test Description', 'id': '123'}]
        }
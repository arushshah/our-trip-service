from models import User, Trip

def add_user(client):
     client.post("/users/create-user", json={
          "user_username": "test_user",
          "user_first_name": "Test",
          "user_last_name": "User",
          "user_email": "test@email.com",
          "user_password": "test123"
     })

def test_create_trip_no_host(client):
    response = client.post("/trips/create-trip", json={
        "trip_name": "test_trip",
        "trip_description": "Test Trip",
        "trip_start_date": "10/10/2021",
        "trip_end_date": "10/20/2021",
        "trip_hostname": "test_user"
    })

    print(response.json)
    assert response.status_code == 404
    assert response.json == {"error": "Host user not found."}

    assert Trip.query.filter_by(name="test_trip").count() == 0

def test_create_trip_success(client):

    # Create a user
    add_user(client)

    response = client.post("/trips/create-trip", json={
        "trip_name": "test_trip",
        "trip_description": "Test Trip",
        "trip_start_date": "10/10/2021",
        "trip_end_date": "10/20/2021",
        "trip_hostname": "test_user"
    })

    assert response.status_code == 201
    assert response.json == {"message": "Trip created successfully."}

    trip = Trip.query.filter_by(name="test_trip").first()

    assert trip.name == "test_trip"
    assert trip.description == "Test Trip"
    assert trip.host_username == "test_user"
    assert trip.start_date.strftime("%m/%d/%Y") == "10/10/2021"
    assert trip.end_date.strftime("%m/%d/%Y") == "10/20/2021"

def test_update_trip(client):
    
        add_user(client)

        response = client.post("/trips/create-trip", json={
            "trip_name": "test_trip",
            "trip_description": "Test Trip",
            "trip_start_date": "10/10/2021",
            "trip_end_date": "10/20/2021",
            "trip_hostname": "test_user"
        })

        assert response.status_code == 201
        assert response.json == {"message": "Trip created successfully."}

        trip = Trip.query.filter_by(name="test_trip").first()
        
        assert trip.name == "test_trip"
        assert trip.description == "Test Trip"
        assert trip.host_username == "test_user"
        assert trip.start_date.strftime("%m/%d/%Y") == "10/10/2021"
        assert trip.end_date.strftime("%m/%d/%Y") == "10/20/2021"

        response = client.put("/trips/update-trip", json={
            "trip_id": trip.id,
            "trip_name": "updated_trip",
            "trip_description": "Updated Trip",
            "trip_start_date": "10/15/2021",
            "trip_end_date": "10/25/2021",
            "trip_hostname": "test_user"
        })
        
        assert response.status_code == 200
        assert response.json == {"message": "Trip updated successfully."}

        trip = Trip.query.filter_by(name="updated_trip").first()

        assert trip.name == "updated_trip"
        assert trip.description == "Updated Trip"
        assert trip.host_username == "test_user"
        assert trip.start_date.strftime("%m/%d/%Y") == "10/15/2021"
        assert trip.end_date.strftime("%m/%d/%Y") == "10/25/2021"
from models import User, Trip, TripGuest, UserUpload

def test_trip_model():
    trip = Trip(name="Test Trip", description="Test description", host_username="test_user", start_date="2021-01-01", end_date="2021-01-10")
    assert trip.name == "Test Trip"
    assert trip.description == "Test description"
    assert trip.host_username == "test_user"
    assert trip.start_date == "2021-01-01"
    assert trip.end_date == "2021-01-10"

def test_user_model():
    user = User(username="test_user", first_name="Test", last_name="User", email="test_email@gmail.com", password="test_password")
    assert user.username == "test_user"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.email == "test_email@gmail.com"
    assert user.password == "test_password"

def test_trip_guest_model():
    trip_guest = TripGuest(trip_id=1, guest_username="test_user", is_host=False)
    assert trip_guest.trip_id == 1
    assert trip_guest.guest_username == "test_user"
    assert trip_guest.is_host == False

def test_user_upload_model():
    user_upload = UserUpload(user_id="test_user", trip_id=1, file_name="test_file.jpg", s3_url="https://s3.amazonaws.com/test_bucket/test_file.jpg")
    assert user_upload.user_id == "test_user"
    assert user_upload.trip_id == 1
    assert user_upload.file_name == "test_file.jpg"
    assert user_upload.s3_url == "https://s3.amazonaws.com/test_bucket/test_file.jpg"
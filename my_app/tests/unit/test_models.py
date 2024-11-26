from models import db, User, Trip, TripGuest, UserUpload, ItineraryEntry, LocationCategory, TripExpenseShare, TripExpense, TripTodo, TripLocation

def test_trip_model():
    trip = Trip(name="Test Trip", description="Test description", host_id="test_user", start_date="2021-01-01", end_date="2021-01-10")
    assert trip.name == "Test Trip"
    assert trip.description == "Test description"
    assert trip.host_id == "test_user"
    assert trip.start_date == "2021-01-01"
    assert trip.end_date == "2021-01-10"

def test_user_model():
    user = User(id="test_user", first_name="Test", last_name="User", phone_number="1234567890")
    assert user.id == "test_user"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.phone_number == "1234567890"
    assert user.created_at == None

def test_trip_guest_model():
    trip_guest = TripGuest(trip_id=1, guest_id="test_user", is_host=False, rsvp_status="INVITED")
    assert trip_guest.trip_id == 1
    assert trip_guest.guest_id == "test_user"
    assert trip_guest.is_host == False
    assert trip_guest.rsvp_status == "INVITED"

def test_user_upload_model():
    user_upload = UserUpload(upload_user_id="test_user", trip_id=1, file_name="test_file.jpg", s3_url="https://s3.amazonaws.com/test_bucket/test_file.jpg", document_category="travel")
    assert user_upload.upload_user_id == "test_user"
    assert user_upload.document_category == "travel"
    assert user_upload.trip_id == 1
    assert user_upload.file_name == "test_file.jpg"
    assert user_upload.s3_url == "https://s3.amazonaws.com/test_bucket/test_file.jpg"

def test_itinerary_entry_model():
    itinerary_entry = ItineraryEntry(trip_id=1, description="Test description", date="2021-01-01")
    assert itinerary_entry.trip_id == 1
    assert itinerary_entry.description == "Test description"
    assert itinerary_entry.date == "2021-01-01"

def test_location_category_model():
    location_category = LocationCategory(name="Test Category", trip_id=1)
    assert location_category.name == "Test Category"
    assert location_category.trip_id == 1

def test_trip_expense_share_model():
    trip_expense_share = TripExpenseShare(trip_id=1, expense_id=1, user_id="test_user", amount=100.00)
    assert trip_expense_share.trip_id == 1
    assert trip_expense_share.user_id == "test_user"
    assert trip_expense_share.amount == 100.00
    assert trip_expense_share.expense_id == 1

def test_trip_expense_model():
    trip_expense = TripExpense(trip_id=1, user_id="test_user", title="Test Expense", amount=100.00, settled=False)
    assert trip_expense.trip_id == 1
    assert trip_expense.user_id == "test_user"
    assert trip_expense.title == "Test Expense"
    assert trip_expense.amount == 100.00
    assert trip_expense.settled == False

def test_trip_todo_model():
    trip_todo = TripTodo(trip_id=1, text="Test Todo", checked=True, last_updated_at="2021-01-01")
    assert trip_todo.trip_id == 1
    assert trip_todo.text == "Test Todo"
    assert trip_todo.checked == True
    assert trip_todo.last_updated_at == "2021-01-01"

def test_trip_location_model():
    trip_location = TripLocation(trip_id=1, place_id="123", user_id="test_id", name="Test Location", latitude=0.0, longitude=0.0, category_id=1)
    assert trip_location.trip_id == 1
    assert trip_location.name == "Test Location"
    assert trip_location.latitude == 0.0
    assert trip_location.longitude == 0.0
    assert trip_location.place_id == "123"
    assert trip_location.user_id == "test_id"
    assert trip_location.category_id == 1
    
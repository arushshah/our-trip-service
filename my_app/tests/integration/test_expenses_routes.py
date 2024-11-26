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

def add_expense_to_trip():
    expense = TripExpense(
        id=1,
        trip_id=1,
        user_id="test_user",
        title="Test Expense",
        amount=100,
        settled=False,
        created_at=datetime(2024, 11, 8),
        updated_at=datetime(2024, 11, 8)
    )
    expense_share = TripExpenseShare(
        id=1,
        expense_id=1,
        user_id="test_user",
        amount=100,
        trip_id=1
    )
    db.session.add(expense)
    db.session.add(expense_share)
    db.session.commit()

@patch("firebase_admin.auth.verify_id_token")
def test_add_expense(mock_verify_id_token, client, app_context):
    create_user()
    create_trip()
    add_user_to_trip()

    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }

    response = client.post("/expenses/add-expense", json={
        "trip_id": 1,
        "expenseId": 1,
        "userId": "test_user",
        "title": "Test Expense",
        "amount": 100,
        "settled": False,
        "createdDate": "2024-11-08T00:00:00.000Z",
        "usersInvolved": [
            {"selectedUserId": "test_user", "amount": 100},
        ]
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 201
    assert response.json == {"message": "Expense added successfully."}

    expense = TripExpense.query.filter_by(id=1).first()
    assert expense.trip_id == 1
    assert expense.user_id == "test_user"
    assert expense.title == "Test Expense"
    assert expense.amount == 100
    assert expense.settled == False

    expense_share = TripExpenseShare.query.filter_by(expense_id=1).first()
    assert expense_share.user_id == "test_user"
    assert expense_share.amount == 100
    assert expense_share.trip_id == 1

@patch("firebase_admin.auth.verify_id_token")
def test_update_expense(mock_verify_id_token, client, app_context):
    create_user()
    create_trip()
    add_user_to_trip()
    add_expense_to_trip()

    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }

    response = client.put("/expenses/update-expense", json={
        "trip_id": 1,
        "expense_id": 1,
        "user_id": "test_user",
        "title": "Updated Test Expense",
        "amount": 200,
        "usersInvolved": [
            {"selectedUserId": "test_user", "amount": 200},
        ]
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json == {"message": "Expense updated successfully."}

    expense = TripExpense.query.filter_by(id=1).first()
    assert expense.trip_id == 1
    assert expense.user_id == "test_user"
    assert expense.title == "Updated Test Expense"
    assert expense.amount == 200

    expense_share = TripExpenseShare.query.filter_by(expense_id=1).first()
    assert expense_share.user_id == "test_user"
    assert expense_share.amount == 200

@patch("firebase_admin.auth.verify_id_token")
def test_get_expenses(mock_verify_id_token, client, app_context):
    create_user()
    create_trip()
    add_user_to_trip()
    add_expense_to_trip()

    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }

    response = client.get("/expenses/get-expenses?trip_id=1", headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json == {
        'expenses': [{'amount': 100.0, 'createdDate': 'Nov 08', 'expenseId': 1, 'settled': False, 'title': 'Test Expense', 'updatedDate': 'Nov 08', 'userFirstName': 'Test', 'userId': 'test_user', 'userLastName': 'User', 'usersInvolved': [{'amount': 100.0, 'firstName': 'Test', 'lastName': 'User', 'selectedUserId': 'test_user'}]}]
        }

@patch("firebase_admin.auth.verify_id_token")
def test_delete_expense(mock_verify_id_token, client, app_context):
    create_user()
    create_trip()
    add_user_to_trip()
    add_expense_to_trip()

    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }

    response = client.delete("/expenses/delete-expense", json={
        "trip_id": 1,
        "expense_id": 1
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 200
    assert response.json == {"message": "Expense deleted successfully."}

    expense = TripExpense.query.filter_by(id=1).first()
    assert expense is None

    expense_share = TripExpenseShare.query.filter_by(expense_id=1).first()
    assert expense_share is None
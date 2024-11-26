from unittest.mock import patch
from models import User

@patch("firebase_admin.auth.verify_id_token")
def test_create_user(mock_verify_id_token, client, app_context):

    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }
    response = client.post("/users/create-user", json={
        "firstName": "Test",
        "lastName": "User",
        "phoneNumber": "1234567890"
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 201
    assert response.json == {"message": "User created successfully"}

    user = User.query.filter_by(id="test_user").first()
    assert user.id == "test_user"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.phone_number == "+11234567890"

@patch("firebase_admin.auth.verify_id_token")
def test_create_user_duplicate_phone_number(mock_verify_id_token, client, app_context):

    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }
    response = client.post("/users/create-user", json={
        "firstName": "Test",
        "lastName": "User",
        "phoneNumber": "1234567890"
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 201
    assert response.json == {"message": "User created successfully"}

    response = client.post("/users/create-user", json={
        "firstName": "Test2",
        "lastName": "User2",
        "phoneNumber": "1234567890"
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 400
    assert response.json == {"error": "Phone number already registered."}
    assert User.query.filter_by(phone_number="+11234567890").count() == 1

@patch("firebase_admin.auth.verify_id_token")
def test_validate_user(mock_verify_id_token, client, app_context):
    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }
    response = client.post("/users/create-user", json={
        "firstName": "Test",
        "lastName": "User",
        "phoneNumber": "+11234567890"
    }, headers={"Authorization": "Bearer test_token"})

    assert response.status_code == 201
    assert response.json == {"message": "User created successfully"}

    response = client.post("/users/validate-user", json={"phone_number": "+11234567890"},
                           headers={"Authorization": "Bearer test_token"})
    assert response.status_code == 200
    assert response.json == {'firstName': 'Test', 'lastName': 'User', 'message': 'User validated successfully.', 'phoneNumber': '+11234567890', 'userId': 'test_user'}

@patch("firebase_admin.auth.verify_id_token")

def test_validate_user_not_found(mock_verify_id_token, client, app_context):
    mock_verify_id_token.return_value = {
        'user_id': 'test_user', 'phone_number': '+11234567890'
    }
    response = client.post("/users/validate-user", json={"phone_number": "+11234567890"},
                           headers={"Authorization": "Bearer test_token"})
    assert response.status_code == 401
    assert response.json == {'error': 'User does not exist.'}
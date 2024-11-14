from models import User

def test_create_user(client):
    response = client.post("/users/create-user", json={
        "user_username": "test_user",
        "user_first_name": "Test",
        "user_last_name": "User",
        "user_email": "test@email.com",
        "user_password": "test123"
    })

    assert response.status_code == 201
    assert response.json == {"message": "User created successfully"}

    user = User.query.filter_by(username="test_user").first()
    assert user.username == "test_user"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.email == "test@email.com"

def test_create_user_duplicate_email(client):
    response = client.post("/users/create-user", json={
        "user_username": "test_user",
        "user_first_name": "Test",
        "user_last_name": "User",
        "user_email": "test@email.com",
        "user_password": "test123"
    })
    assert response.status_code == 201
    assert response.json == {"message": "User created successfully"}

    response = client.post("/users/create-user", json={
        "user_username": "test_user2",
        "user_first_name": "Test2",
        "user_last_name": "User2",
        "user_email": "test@email.com",
        "user_password": "test123"
    })
    assert response.status_code == 400
    assert response.json == {"error": "Email already exists."}

    assert User.query.filter_by(username="test_user").count() == 1

def test_create_user_duplicate_username(client):
    response = client.post("/users/create-user", json={
        "user_username": "test_user",
        "user_first_name": "Test",
        "user_last_name": "User",
        "user_email": "test@email.com",
        "user_password": "test123"
    })
    assert response.status_code == 201
    assert response.json == {"message": "User created successfully"}

    response = client.post("/users/create-user", json={
        "user_username": "test_user",
        "user_first_name": "Test2",
        "user_last_name": "User2",
        "user_email": "test2@email.com",
        "user_password": "test123"
    })

    assert response.status_code == 400
    assert response.json == {"error": "Username already exists."}
    assert User.query.filter_by(username="test_user").count() == 1
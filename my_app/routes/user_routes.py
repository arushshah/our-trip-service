import bcrypt
from flask import Blueprint, request, jsonify, current_app as app
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from my_app.models import User, db

users_bp = Blueprint('users', __name__)

def init_jwt(app):
    jwt = JWTManager(app)
    return jwt

@users_bp.route('/authenticate', methods=['POST'])
def authenticate_user():
        data = request.json
        user_username = data.get('user_username')
        user_password = data.get('user_password')
    
        user = User.query.filter_by(username=user_username).first()
        if not user:
            return jsonify({"error": "Invalid username."}), 401
    
        if bcrypt.checkpw(user_password.encode('utf-8'), user.password.encode('utf-8')):
            access_token = create_access_token(identity=user.username)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"error": "Incorrect password."}), 401

@users_bp.route('/validate-token', methods=['POST'])
@jwt_required()
def validate_token():
    current_user = get_jwt_identity()
    return jsonify({"message": "Token is valid", "user": current_user}), 200

@users_bp.route('/create-user', methods=['POST'])
def create_user():
    
    data = request.json
    user_username = data.get('user_username')
    user_first_name = data.get('user_first_name')
    user_last_name = data.get('user_last_name')
    user_email = data.get('user_email')
    user_password = data.get('user_password')

    # Hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), salt).decode('utf-8')

    try:
        
        user = User.query.filter_by(username=user_username).first()
        if user:
            return jsonify({"error": "Username already exists."}), 400
        
        user = User.query.filter_by(email=user_email).first()
        if user:
            return jsonify({"error": "Email already exists."}), 400


        # If the username is unique, proceed to create the user
        new_user = User(
            username=user_username,
            first_name=user_first_name,
            last_name=user_last_name,
            email=user_email,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while adding the user to the DB."}), 500

    return jsonify({f"message": "User created successfully"}), 201
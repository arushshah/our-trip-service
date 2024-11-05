from flask import Blueprint, request, jsonify
from my_app.models import User, db
from my_app.utils import token_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/authenticate', methods=['POST'])
def authenticate_user():
        data = request.json
        user_id = data.get('user_id')
    
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({"error": "Phone number does not exist"}), 401

@users_bp.route('/create-user', methods=['POST'])
@token_required
def create_user(decoded_token):
    print(decoded_token)
    data = request.json
    phone_number = data.get('phoneNumber')
    first_name = data.get('firstName')
    last_name = data.get('lastName')

    try:
        user = User.query.filter_by(user_id=phone_number).first()
        if user:
            return jsonify({"error": "User already exists."}), 400

        # If the user id is unique, proceed to create the user
        new_user = User(
            user_id=phone_number,
            first_name=first_name,
            last_name=last_name,
        )
        db.session.add(new_user)
        db.session.commit()

    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while adding the user to the DB."}), 500

    return jsonify({f"message": "User created successfully"}), 201

@users_bp.route('/validate-user', methods=['POST', 'OPTIONS'])
def validate_user():
    if request.method == 'OPTIONS':
         return '', 200
    print(request)
    phone_number = request.json.get('phone_number')

    user = User.query.filter_by(user_id=phone_number).first()
    if not user:
        return jsonify({"error": "Phone number does not exist."}), 401
    return jsonify({"message": "User validated successfully.", "phoneNumber": user.user_id, "firstName": user.first_name, "lastName": user.last_name}), 200
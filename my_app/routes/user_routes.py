from flask import Blueprint, request, jsonify, current_app as app
from flask_cors import cross_origin
from models import User, db
from .utils import token_required, get_request_data

users_bp = Blueprint('users', __name__)

@users_bp.route('/create-user', methods=['POST'])
@cross_origin()
@token_required
def create_user(token):
    
    app.logger.info("users/create-user")
    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    phone_number = data['phone_number']
    first_name = data['firstName']
    last_name = data['lastName']

    try:
        user = User.query.filter_by(phone_number=phone_number).first()
        if user:
            app.logger.debug("Error, phone number already registered")
            return jsonify({"error": "Phone number already registered."}), 400

        # If the user id is unique, proceed to create the user
        new_user = User(
            id=user_id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
        )
        db.session.add(new_user)
        db.session.commit()

    except Exception as e:
        app.logger.error("Failed to add user to db: ", e)
        return jsonify({"error": "An error occurred while adding the user to the DB."}), 500

    return jsonify({f"message": "User created successfully"}), 201

@users_bp.route('/validate-user', methods=['POST', 'OPTIONS'])
@cross_origin()
def validate_user():
    app.logger.info("users/validate-user")

    data = get_request_data()
    app.logger.debug(data)
    phone_number = data['phone_number']

    user = User.query.filter_by(phone_number=phone_number).first()
    if not user:
        app.logger.error("User does not exist")
        return jsonify({"error": "User does not exist."}), 401
    return jsonify({"message": "User validated successfully.", "phoneNumber": user.phone_number, "firstName": user.first_name, "lastName": user.last_name, "userId": user.id}), 200
from functools import wraps
from flask import request, jsonify, current_app as app
from functools import wraps
from firebase_admin import auth
from models import Trip, TripGuest, User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({"error": "Token is missing."}), 401
        try:
            decoded_token = auth.verify_id_token(token)
        except Exception as e:
            app.logger.error(e)
            return jsonify({"message": "Token is invalid!", "error": str(e)}), 401
        return f(decoded_token, *args, **kwargs)
    return decorated

def get_request_data(token=None):
    if request.method == 'GET':
        tmp = request.args.to_dict()
        tmp['phone_number'] = token['phone_number']
        tmp['user_id'] = token['user_id']
        return tmp
    elif request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
        if request.get_json():
            if token:
                return {**request.get_json(), "phone_number": token['phone_number'], "user_id": token['user_id']}
            else:
                return request.get_json()
        return {}

def validate_user_trip(user_id, trip_id):
    try:
        trip_id = int(trip_id)
    except ValueError:
        return False, jsonify({"error": "Invalid trip ID."})

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return False, jsonify({"error": "User not found."})
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return False, jsonify({"error": "Trip not found."})
    guest = TripGuest.query.filter_by(trip_id=trip_id, guest_id=user_id).first()
    if not guest:
        return False, jsonify({"error": "User is not a guest of this trip."})
    return True, None
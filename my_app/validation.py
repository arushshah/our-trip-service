from flask import jsonify
from my_app.models.trip import Trip
from my_app.models.user import User

def validate_user_id(user_id):
    if not user_id:
        return jsonify({"error": "User id is required."}), 404
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"error": "User not found."}), 404
    return "valid"

def validate_trip_id(trip_id):
    try:
        trip_id = int(trip_id)
    except ValueError:
        return jsonify({"error": "Invalid trip ID."}), 400
    if not trip_id:
        return jsonify({"error": "Trip id is required."}), 404
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404
    return "valid"
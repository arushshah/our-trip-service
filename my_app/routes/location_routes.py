from flask import Blueprint, jsonify, request
from flask import current_app as app
from flask_cors import cross_origin
from models import Trip, db, TripGuest, User, TripLocation
from .utils import token_required, get_request_data

trip_locations_bp = Blueprint('trip_locations', __name__)

@trip_locations_bp.route('/add-location', methods=['POST'])
@cross_origin()
@token_required
def add_location(token):
    app.logger.info("trip_locations/add-location")

    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    trip_id = data['trip_id']
    lat = data['lat']
    lng = data['lng']
    name = data['name']
    place_id = data['place_id']
    category = data['category']

    try:
        trip_id = int(trip_id)
    except ValueError:
        app.logger.error("Invalid input. 400 Error")
        return jsonify({"error": "Invalid trip ID."}), 400
    
    is_host = False

    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404

    # Check if the user is already a guest
    existing_guest = TripGuest.query.filter_by(trip_id=trip_id, guest_id=user_id).first()
    if existing_guest:
        return jsonify({"error": "User is already a guest of this trip."}), 409  # HTTP 409 Conflict
    
    # check if the user exists
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found."}), 404

    try:
        # Add the location to the trip
        trip_location = TripLocation(trip_id=trip_id, user_id=user_id, latitude=lat, longitude=lng, name=name, place_id=place_id, category=category)
        db.session.add(trip_location)
        db.session.commit()

    except Exception as e:
        app.logger.error(f"Error adding guest to trip: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while adding the user to the DB."}), 500

    return jsonify({"message": "Guest added successfully."}), 201
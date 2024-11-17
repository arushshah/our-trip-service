from datetime import datetime
from flask import Blueprint, request, jsonify, current_app as app
from flask_cors import cross_origin
from models import User, db, Trip, TripGuest, TripExpense, TripExpenseShare, TripLocation
from .utils import token_required, get_request_data

expenses_bp = Blueprint('locations', __name__)

@expenses_bp.route('/add-location', methods=['POST'])
@cross_origin()
@token_required
def add_expense(token):
    
    app.logger.info("expenses/add-expense")
    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    trip_id = data['trip_id']
    latitude = data['latitude']
    longitude = data['longitude']

    try:
        trip_id = int(trip_id)
    except ValueError:
        app.logger.error("Invalid input. 400 Error")
        return jsonify({"error": "Invalid trip ID."}), 400
    
    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404
    
    # Check if the user is a guest of the trip
    guest = TripGuest.query.filter_by(trip_id=trip_id, guest_id=user_id).first()
    if not guest:
        return jsonify({"error": "User is not a guest of this trip."}), 403
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        app.logger.error("Invalid input. 400 Error")
        return jsonify({"error": "Invalid location."}), 400
    
    # Add the location to the trip

    try:
        new_location = TripLocation(
            trip_id=trip_id,
            guest_id=user_id,
            latitude=latitude,
            longitude=longitude
        )
        db.session.add(new_location)
        db.session.commit()
    except Exception as e:
        app.logger.error("Error adding location: %s", e)
        return jsonify({"error": "Error adding location."}), 500
    
    return jsonify({"message": "Location added successfully."}), 200

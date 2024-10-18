from datetime import datetime
from flask import Blueprint, jsonify, request
from flask import current_app as app
from my_app.models import User, Trip, db, TripGuest

trips_bp = Blueprint('trips', __name__)

@trips_bp.route('/create-trip', methods=['POST'])
def create_trip():
    data = request.json

    # Extract data from request
    trip_name = data.get('trip_name')
    trip_description = data.get('trip_description')
    trip_hostname = data.get('trip_hostname')
    trip_start_date = data.get('trip_start_date')
    trip_end_date = data.get('trip_end_date')

    # Define date format
    date_format = "%m/%d/%Y"

    # Basic Validations
    if not trip_name or len(trip_name.strip()) == 0:
        return jsonify({"error": "Trip name is required."}), 400

    if not trip_hostname or len(trip_hostname.strip()) == 0:
        return jsonify({"error": "Host username is required."}), 400

    if not trip_start_date or not trip_end_date:
        return jsonify({"error": "Start and end dates are required."}), 400

    try:
        # Validate and parse dates
        trip_start_date = datetime.strptime(trip_start_date, date_format)
        trip_end_date = datetime.strptime(trip_end_date, date_format)

        # Check if start date is before end date
        if trip_start_date > trip_end_date:
            return jsonify({"error": "Start date cannot be later than end date."}), 400

    except ValueError:
        return jsonify({"error": "Invalid date format. Use MM/DD/YYYY."}), 400

    host = User.query.filter_by(username=trip_hostname).first()
    if not host:
        return jsonify({"error": "Host user not found."}), 404

    try:
        # Create a new trip
        new_trip = Trip(
            name=trip_name,
            description=trip_description,
            host_username=trip_hostname,
            start_date=trip_start_date,
            end_date=trip_end_date
        )
        db.session.add(new_trip)
        db.session.commit()

    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while adding the trip to the DB."}), 500

    return jsonify({"message": "Trip created successfully."}), 201

# endpoint to update a trip - all the fields for the trip can be changed except for the trip id. all the fields to update are optional, if a field is not provided i dont want to update it. if the host username is updated, i want to make sure that the new host username exists in the users table and i want to update the is_host field in the trip_guests table accordingly.
@trips_bp.route('/update-trip', methods=['PUT'])
def update_trip():
    data = request.json
    trip_id = data.get('trip_id')

    if not trip_id:
        return jsonify({"error": "Trip ID is required."}), 400

    try:
        trip_id = int(trip_id)
    except ValueError:
        return jsonify({"error": "Invalid trip ID."}), 400

    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404

    # Extract data from request
    trip_name = data.get('trip_name')
    trip_description = data.get('trip_description')
    trip_hostname = data.get('trip_hostname')
    trip_start_date = data.get('trip_start_date')
    trip_end_date = data.get('trip_end_date')

    # Define date format
    date_format = "%m/%d/%Y"

    # Validate and parse dates
    if trip_start_date:
        try:
            trip_start_date = datetime.strptime(trip_start_date, date_format)
        except ValueError:
            return jsonify({"error": "Invalid start date format. Use MM/DD/YYYY."}), 400

    if trip_end_date:
        try:
            trip_end_date = datetime.strptime(trip_end_date, date_format)
        except ValueError:
            return jsonify({"error": "Invalid end date format. Use MM/DD/YYYY."}), 400

    # Check if the new host exists
    if trip_hostname:
        new_host = User.query.filter_by(username=trip_hostname).first()
        if not new_host:
            return jsonify({"error": "New host user not found."}), 404
    else:
        return jsonify({"error": "Host username is required."}), 400

    try:
        # Update the trip
        if trip_name:
            trip.name = trip_name
        if trip_description:
            trip.description = trip_description
        if trip_hostname:
            trip.host_username = trip_hostname
            # Update the is_host field in the trip_guests table
            TripGuest.query.filter_by(trip_id=trip_id, guest_username=trip.host_username).update({"is_host": False})
            TripGuest.query.filter_by(trip_id=trip_id, guest_username=trip_hostname).update({"is_host": True})
        if trip_start_date:
            trip.start_date = trip_start_date
        if trip_end_date:
            trip.end_date = trip_end_date

        db.session.commit()
        return jsonify({"message": "Trip updated successfully."}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while updating the trip."}), 500
    
# create a function called delete_trip, that takes in a user id and a trip id and deletes the trip associated with the user as well as all trip guests associated with the trip.
@trips_bp.route('/delete-trip', methods=['DELETE'])
def delete_trip():
    user_id = request.args.get('host_username')
    trip_id = request.args.get('trip_id')

    # Check if the user exists
    user = User.query.filter_by(username=user_id).first()
    if not user:
        return jsonify({"error": "User not found."}), 404

    try:
        trip_id = int(trip_id)
    except ValueError:
        return jsonify({"error": "Invalid trip ID."}), 400
    
    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404

    # Check if the user is the host of the trip
    if trip.host_username != user.username:
        return jsonify({"error": "User is not the host of this trip."}), 403

    try:
        TripGuest.query.filter_by(trip_id=trip_id).delete()
        Trip.query.filter_by(id=trip_id).delete()
        db.session.commit()
        return jsonify({"message": "Trip deleted successfully."}), 200
    except Exception as e:
        app.logger.error(f"Error deleting trip: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the trip."}), 500
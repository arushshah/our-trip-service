from flask import Blueprint, jsonify, request
from flask import current_app as app
from my_app.models import Trip, db, TripGuest
from my_app.models.user import User

trip_guests_bp = Blueprint('trip_guests', __name__)

@trip_guests_bp.route('/add-trip-guest', methods=['POST'])
def add_trip_guest():
    data = request.json
    user_username = data.get('trip_guest_username')
    trip_id = data.get('trip_id')

    if not user_username or not trip_id:
        return jsonify({"error": "Invalid input."}), 400

    try:
        trip_id = int(trip_id)
    except ValueError:
        return jsonify({"error": "Invalid trip ID."}), 400
    
    is_host = False

    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404

    # Check if the user is already a guest
    existing_guest = TripGuest.query.filter_by(trip_id=trip_id, guest_username=user_username).first()
    if existing_guest:
        return jsonify({"error": "User is already a guest of this trip."}), 409  # HTTP 409 Conflict

    # Set 'is_host' if the user is the host of the trip
    if trip.host_username == user_username:
        is_host = True

    try:
        # Add the guest to the trip
        trip_guest = TripGuest(trip_id=trip_id, guest_username=user_username, is_host=is_host)
        db.session.add(trip_guest)
        db.session.commit()

    except Exception as e:
        app.logger.error(f"Error adding guest to trip: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while adding the user to the DB."}), 500

    return jsonify({"message": "Guest added successfully."}), 201

# create a function called get_trip_guests that takes in a trip id and returns a list of guests associated with the trip.
@trip_guests_bp.route('/get-trip-guests', methods=['GET'])
def get_trip_guests():
    trip_id = request.args.get('trip_id')

    try:
        trip_id = int(trip_id)
    except ValueError:
        return jsonify({"error": "Invalid trip ID."}), 400

    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404

    # Get all guests associated with the trip
    guests = TripGuest.query.filter_by(trip_id=trip_id).all()
    print(guests)

    guest_list = []
    for guest in guests:
        user = User.query.filter_by(username=guest.guest_username).first()
        print(user)
        guest_list.append({
            "guest_username": guest.guest_username,
            "is_host": guest.is_host,
            "guest_first_name": user.first_name,
            "guest_last_name": user.last_name
        })

    return jsonify({"guests": guest_list}), 200    
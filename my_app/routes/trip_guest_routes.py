from flask import Blueprint, jsonify, request
from flask import current_app as app
from flask_cors import cross_origin
from my_app.models import Trip, db, TripGuest
from my_app.models.user import User
from my_app.utils import token_required

trip_guests_bp = Blueprint('trip_guests', __name__)

@trip_guests_bp.route('/add-trip-guest', methods=['POST'])
@token_required
def add_trip_guest(token):
    user_id = token['phone_number']
    data = request.json
    trip_id = data.get('trip_id')
    print(data)

    if not user_id or not trip_id:
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
    existing_guest = TripGuest.query.filter_by(trip_id=trip_id, guest_user_id=user_id).first()
    if existing_guest:
        return jsonify({"error": "User is already a guest of this trip."}), 409  # HTTP 409 Conflict
    
    # check if the user exists
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"error": "User not found."}), 404

    # Set 'is_host' if the user is the host of the trip
    if trip.host_user_id == user_id:
        is_host = True

    try:
        # Add the guest to the trip
        trip_guest = TripGuest(trip_id=trip_id, guest_user_id=user_id, is_host=is_host)
        db.session.add(trip_guest)
        db.session.commit()

    except Exception as e:
        app.logger.error(f"Error adding guest to trip: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while adding the user to the DB."}), 500

    return jsonify({"message": "Guest added successfully."}), 201

# create a function called get_trip_guests that takes in a trip id and returns a list of guests associated with the trip.
@trip_guests_bp.route('/get-trip-guests', methods=['GET'])
@token_required
def get_trip_guests(token):
    print(token)
    trip_id = request.args.get('trip_id')

    try:
        trip_id = int(trip_id)
    except ValueError:
        return jsonify({"error": "Invalid trip ID."}), 400

    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404

    # Get all guests associated with the trip and whose rsvp status is not 'None'

    guests = TripGuest.query.filter_by(trip_id=trip_id).all()
    print(guests)

    guest_list = []
    for guest in guests:
        user = User.query.filter_by(user_id=guest.guest_user_id).first()
        print("USER: " + str(user))
        guest_list.append({
            "guest_username": guest.guest_user_id,
            "is_host": guest.is_host,
            "guest_first_name": user.first_name,
            "guest_last_name": user.last_name,
            "rsvp_status": guest.rsvp_status.value
        })

    return jsonify({"guests": guest_list}), 200    

@trip_guests_bp.route("/delete-trip-guest", methods=["DELETE"])
@token_required
def delete_trip_guest(token):
    user_id = token["phone_number"]
    data = request.json
    trip_id = data.get("trip_id")

    if not user_id or not trip_id:
        return jsonify({"error": "Invalid input."}), 400

    try:
        trip_id = int(trip_id)
    except ValueError:
        return jsonify({"error": "Invalid trip ID."}), 400

    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404

    # Check if the user is a guest of the trip
    trip_guest = TripGuest.query.filter_by(trip_id=trip_id, guest_user_id=user_id).first()
    if not trip_guest:
        return jsonify({"error": "User is not a guest of this trip."}), 404

    # the host should not be able to delete themselves from the trip
    if trip_guest.is_host:
        return jsonify({"error": "Host cannot delete themselves from the trip."}), 403
    try:
        # Delete the guest from the trip
        db.session.delete(trip_guest)
        db.session.commit()

    except Exception as e:
        app.logger.error(f"Error deleting guest from trip: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the user from the DB."}), 500

    return jsonify({"message": "Guest deleted successfully."}), 200

@trip_guests_bp.route("/update-rsvp-status", methods=["PUT"])
@token_required
def update_rsvp_status(token):
    user_id = token["phone_number"]
    data = request.json
    trip_id = data.get("trip_id")
    rsvp_status = data.get("rsvp_status")

    if not user_id or not trip_id or not rsvp_status:
        return jsonify({"error": "Invalid input."}), 400

    try:
        trip_id = int(trip_id)
    except ValueError:
        return jsonify({"error": "Invalid trip ID."}), 400

    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404

    # Check if the user is a guest of the trip
    trip_guest = TripGuest.query.filter_by(trip_id=trip_id, guest_user_id=user_id).first()
    if not trip_guest:
        return jsonify({"error": "User is not a guest of this trip."}), 404

    # Check if the user is the host of the trip
    if trip.host_user_id == user_id:
        return jsonify({"error": "Host cannot update their RSVP status."}), 403

    # Check if the rsvp status is valid
    if rsvp_status not in ["YES", "NO", "MAYBE"]:
        return jsonify({"error": "Invalid RSVP status."}), 400

    try:
        # Update the rsvp status
        trip_guest.rsvp_status = rsvp_status
        db.session.commit()

    except Exception as e:
        app.logger.error(f"Error updating rsvp status: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the rsvp status."}), 500

    return jsonify({"message": "RSVP status updated successfully."}), 200

@trip_guests_bp.route("/accept-invite", methods=["POST"])
@token_required
def accept_invite(token):
    user_id = token["phone_number"]
    trip_token = request.json.get("trip_token")

    # check if the trip_token exists in the trips table
    trip = Trip.query.filter_by(token=trip_token).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404
    
    # check if the user is already a guest of the trip
    existing_guest = TripGuest.query.filter_by(trip_id=trip.id, guest_user_id=user_id).first()
    if existing_guest:
        return jsonify({"error": "User is already a guest of this trip."}), 409
    
    # add the user as a guest of the trip
    try:
        trip_guest = TripGuest(trip_id=trip.id, guest_user_id=user_id, is_host=False, rsvp_status="INVITED")
        db.session.add(trip_guest)
        db.session.commit()

    except Exception as e:
        app.logger.error(f"Error accepting invite: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while accepting the invite."}), 500

    return jsonify({"message": "Invite accepted successfully.", "trip_id": trip.id}), 200

@trip_guests_bp.route('/get-guest-info/<int:trip_id>', methods=['GET', 'OPTIONS'])
@cross_origin()  # Enable CORS for this route
@token_required
def get_guest_info(token, trip_id):
    if request.method == 'OPTIONS':
         return '', 200

    user_id = token['phone_number']
    guest = TripGuest.query.filter_by(trip_id=trip_id, guest_user_id=user_id).first()
    if not guest:
        return jsonify({"error": "Guest not found"}), 404

    guest_info = {
        "trip_id": guest.trip_id,
        "guest_user_id": guest.guest_user_id,
        "rsvp_status": guest.rsvp_status.value,
        "is_host": guest.is_host
    }

    return jsonify({"guest": guest_info}), 200

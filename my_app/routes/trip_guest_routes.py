from flask import Blueprint, jsonify, request
from flask import current_app as app
from flask_cors import cross_origin
from models import Trip, db, TripGuest, User
from .utils import token_required, get_request_data

trip_guests_bp = Blueprint('trip_guests', __name__)

@trip_guests_bp.route('/add-trip-guest', methods=['POST'])
@cross_origin()
@token_required
#@check_required_json_data(['trip_id'])
def add_trip_guest(token):
    app.logger.info("trip_guests/add-trip-guest")

    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['phone_number']
    trip_id = data['trip_id']

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

    # Set 'is_host' if the user is the host of the trip
    if trip.host_id == user_id:
        is_host = True

    try:
        # Add the guest to the trip
        trip_guest = TripGuest(trip_id=trip_id, guest_id=user_id, is_host=is_host)
        db.session.add(trip_guest)
        db.session.commit()

    except Exception as e:
        app.logger.error(f"Error adding guest to trip: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while adding the user to the DB."}), 500

    return jsonify({"message": "Guest added successfully."}), 201

# create a function called get_trip_guests that takes in a trip id and returns a list of guests associated with the trip.
@trip_guests_bp.route('/get-trip-guests', methods=['GET'])
@cross_origin()
@token_required
#@check_required_args_data(['trip_id'])
def get_trip_guests(token):
    app.logger.info("trip_guests/get-trip-guests")
    data = get_request_data(token)
    app.logger.debug(data)

    trip_id = data['trip_id']

    try:
        trip_id = int(trip_id)
    except ValueError as e:
        app.logger.error(e)
        return jsonify({"error": "Invalid trip ID."}), 400

    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404

    # Get all guests associated with the trip and whose rsvp status is not 'None'

    guests = TripGuest.query.filter_by(trip_id=trip_id).all()

    guest_list = []
    for guest in guests:
        user = User.query.filter_by(id=guest.guest_id).first()
        guest_list.append({
            "guest_username": guest.guest_id,
            "is_host": guest.is_host,
            "guest_first_name": user.first_name,
            "guest_last_name": user.last_name,
            "rsvp_status": guest.rsvp_status.value
        })

    return jsonify({"guests": guest_list}), 200    

@trip_guests_bp.route("/delete-trip-guest", methods=["DELETE"])
@cross_origin()
@token_required
#@check_required_json_data(["trip_id"])
def delete_trip_guest(token):
    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data["user_id"]
    trip_id = data["trip_id"]

    try:
        trip_id = int(trip_id)
    except ValueError as e:
        app.logger.error(e)
        return jsonify({"error": "Invalid trip ID."}), 400

    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404

    # Check if the user is a guest of the trip
    trip_guest = TripGuest.query.filter_by(trip_id=trip_id, guest_id=user_id).first()
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
@cross_origin()
@token_required
#@check_required_json_data(["trip_id", "rsvp_status"])
def update_rsvp_status(token):

    data = get_request_data(token)
    app.logger.debug(data)

    user_id = data["user_id"]
    trip_id = data["trip_id"]
    rsvp_status = data["rsvp_status"]

    try:
        trip_id = int(trip_id)
    except ValueError as e:
        app.logger.error(e)
        return jsonify({"error": "Invalid trip ID."}), 400

    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404

    # Check if the user is a guest of the trip
    trip_guest = TripGuest.query.filter_by(trip_id=trip_id, guest_id=user_id).first()
    if not trip_guest:
        return jsonify({"error": "User is not a guest of this trip."}), 404

    # Check if the user is the host of the trip
    if trip.host_id == user_id:
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
@cross_origin()
@token_required
#@check_required_json_data(["trip_token"])
def accept_invite(token):
    data = get_request_data(token)
    app.logger.debug(data)
    user_id = data["user_id"]
    trip_token = data["trip_token"]

    # check if the trip_token exists in the trips table
    trip = Trip.query.filter_by(token=trip_token).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404
    
    # check if the user is already a guest of the trip
    existing_guest = TripGuest.query.filter_by(trip_id=trip.id, guest_id=user_id).first()
    if existing_guest:
        return jsonify({"error": "User is already a guest of this trip."}), 409
    
    # add the user as a guest of the trip
    try:
        trip_guest = TripGuest(trip_id=trip.id, guest_id=user_id, is_host=False, rsvp_status="INVITED")
        db.session.add(trip_guest)
        db.session.commit()

    except Exception as e:
        app.logger.error(f"Error accepting invite: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while accepting the invite."}), 500

    return jsonify({"message": "Invite accepted successfully.", "trip_id": trip.id}), 200

@trip_guests_bp.route('/get-guest-info', methods=['GET', 'OPTIONS'])
@cross_origin()
@token_required
#@check_required_args_data(['trip_id'])
def get_guest_info(token):
    app.logger.info("trip_guests/get-guest-info")
    data = get_request_data(token)
    app.logger.debug(data)

    trip_id = data['trip_id']
    user_id = data['user_id']

    guest = TripGuest.query.filter_by(trip_id=trip_id, guest_id=user_id).first()
    if not guest:
        return jsonify({"error": "Guest not found"}), 404

    guest_info = {
        "trip_id": guest.trip_id,
        "guest_user_id": guest.guest_id,
        "rsvp_status": guest.rsvp_status.value,
        "is_host": guest.is_host
    }

    return jsonify({"guest": guest_info}), 200

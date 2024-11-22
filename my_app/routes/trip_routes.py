import base64
from datetime import datetime, timedelta
import hashlib
import os
import uuid
import boto3
from flask import Blueprint, jsonify, request, current_app as app
from flask_cors import cross_origin
from models import User, Trip, db, TripGuest, RsvpStatus, TripTodo, UserUpload, ItineraryEntry, TripExpense, TripExpenseShare, LocationCategory, TripLocation
from .utils import check_required_json_data, get_request_data, token_required
from .user_upload_routes import delete_trip_uploads

trips_bp = Blueprint('trips', __name__)

# TODO: mismatch in user input for trip dates and actual trip dates, also the itinerary default date creation is wrong
@trips_bp.route('/create-trip', methods=['POST'])
@cross_origin()
@token_required
def create_trip(token):
    app.logger.info("trips/create-trip")
    data = get_request_data(token)

    app.logger.debug(data)
    trip_name = data['trip_name']
    trip_description = data['trip_description']
    trip_start_date = data['trip_start_date']
    trip_end_date = data['trip_end_date']

    user_id = data['user_id']

    # Define date format
    date_format = "%m/%d/%Y"

    # Basic Validations
    if not trip_name or len(trip_name.strip()) == 0:
        return jsonify({"error": "Trip name is required."}), 400

    if not trip_start_date or not trip_end_date:
        return jsonify({"error": "Start and end dates are required."}), 400

    try:
        # Validate and parse dates
        trip_start_date = datetime.strptime(trip_start_date, date_format)
        trip_end_date = datetime.strptime(trip_end_date, date_format)

        # Check if start date is before end date
        if trip_start_date > trip_end_date:
            return jsonify({"error": "Start date cannot be later than end date."}), 400

    except ValueError as e:
        app.logger.error(e)
        return jsonify({"error": "Invalid date format. Use MM/DD/YYYY."}), 400

    host = User.query.filter_by(id=user_id).first()
    if not host:
        return jsonify({"error": "Host user not found."}), 404
    
    trip_token = f"{user_id}-{trip_start_date.strftime('%Y%m%d')}-{trip_end_date.strftime('%Y%m%d')}-{uuid.uuid4().hex}"
    token_hash = hashlib.sha256(trip_token.encode()).digest()
    url_safe_token = base64.urlsafe_b64encode(token_hash).decode('utf-8').rstrip("=")

    try:
        # Create a new trip
        new_trip = Trip(
            name=trip_name,
            token=url_safe_token,
            description=trip_description,
            host_id=user_id,
            start_date=trip_start_date,
            end_date=trip_end_date
        )
        
        db.session.add(new_trip)
        db.session.flush()

        # Add the host as a guest to the trip
        new_trip_guest = TripGuest(trip_id=new_trip.id, guest_id=user_id, is_host=True, rsvp_status=RsvpStatus.YES)
        db.session.add(new_trip_guest)

        # Add empty itinerary entries for days of the trip
        delta = trip_end_date - trip_start_date
        for i in range(delta.days + 1):
            itinerary_date = trip_start_date + timedelta(days=i)
            item_id = uuid.uuid4().hex
            itinerary_entry = ItineraryEntry(trip_id=new_trip.id, date=itinerary_date, description='', id=item_id)
            db.session.add(itinerary_entry)

        db.session.commit()  # Commit the new_trip_guest
        return jsonify({"message": "Trip created successfully."}), 201

    except Exception as e:
        app.logger.error(e)
        return jsonify({"error": "An error occurred while adding the trip to the DB."}), 500

#endpoint to get all trips associated with a user. the input arg is a user id and the output is a list of trips associated with the user.
@trips_bp.route('/get-user-trips', methods=['GET'])
@cross_origin()
@token_required
def get_trips(token):
    app.logger.info("trips/get-user-trips")
    data = get_request_data(token)
    app.logger.debug(data)
    user_id = data['user_id']
    # Check if the user exists
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found."}), 404
    
    # Get all trips associated with the user by querying the trip guests table and getting all the trips where the user is a guest.
    # This will return a list of trip IDs
    trip_guests = TripGuest.query.filter_by(guest_id=user_id).all()
    trip_ids = [trip.trip_id for trip in trip_guests]

    # Get all trips filtered by the list of trip IDs
    trips = Trip.query.filter(Trip.id.in_(trip_ids)).all()

    trip_list = []
    for trip in trips:
        trip_list.append({
            "trip_id": trip.id,
            "trip_name": trip.name,
            "trip_description": trip.description,
            "trip_hostname": trip.host_id,
            "trip_start_date": trip.start_date.strftime("%m/%d/%Y"),
            "trip_end_date": trip.end_date.strftime("%m/%d/%Y"),
            "rsvp_status": TripGuest.query.filter_by(trip_id=trip.id, guest_id=user_id).first().rsvp_status.value,
            "trip_token": trip.token
        })

    return jsonify({"trips": trip_list}), 200

# endpoint to get a trip given a trip id. the input arg is a trip id and the output is the trip details.
@trips_bp.route('/get-trip', methods=['GET'])
@cross_origin()
@token_required
def get_trip(token):
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

    trip_details = {
        "trip_id": trip.id,
        "trip_name": trip.name,
        "trip_description": trip.description,
        "trip_hostname": trip.host_id,
        "trip_start_date": trip.start_date.strftime("%m/%d/%Y"),
        "trip_end_date": trip.end_date.strftime("%m/%d/%Y"),
        "trip_token": trip.token
    }
    return jsonify({"trip_details": trip_details}), 200

# endpoint to update a trip - all the fields for the trip can be changed except for the trip id. all the fields to update are optional, if a field is not provided i dont want to update it. if the host username is updated, i want to make sure that the new host username exists in the users table and i want to update the is_host field in the trip_guests table accordingly.
@trips_bp.route('/update-trip', methods=['PUT'])
@cross_origin()
@token_required
def update_trip(token):
    app.logger.info("trips/update-trip")
    data = get_request_data(token)
    app.logger.debug(data)
    
    trip_id = data['trip_id']

    if not trip_id:
        return jsonify({"error": "Trip ID is required."}), 400

    try:
        trip_id = int(trip_id)
    except ValueError as e:
        app.logger.error(e)
        return jsonify({"error": "Invalid trip ID."}), 400

    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404

    # Extract data from request
    trip_name = data.get('trip_name')
    trip_description = data.get('trip_description')
    trip_start_date = data.get('trip_start_date')
    trip_end_date = data.get('trip_end_date')

    # Define date format
    date_format = "%m/%d/%Y"

    # Validate and parse dates
    if trip_start_date:
        try:
            trip_start_date = datetime.strptime(trip_start_date, date_format)
        except ValueError as e:
            app.logger.error(e)
            return jsonify({"error": "Invalid start date format. Use MM/DD/YYYY."}), 400

    if trip_end_date:
        try:
            trip_end_date = datetime.strptime(trip_end_date, date_format)
        except ValueError as e:
            app.logger.error(e)
            return jsonify({"error": "Invalid end date format. Use MM/DD/YYYY."}), 400
    
    # if the trip end date is before the start date, return an error
    if trip_start_date and trip_end_date and trip_start_date > trip_end_date:
        return jsonify({"error": "Start date cannot be later than end date."}), 400

    try:
        # Update the trip
        if trip_name:
            trip.name = trip_name
        if trip_description:
            trip.description = trip_description
        if trip_start_date:
            trip.start_date = trip_start_date
        if trip_end_date:
            trip.end_date = trip_end_date

        db.session.commit()
        return jsonify({"message": "Trip updated successfully."}), 200

    except Exception as e:
        app.logger.error(e)
        return jsonify({"error": "An error occurred while updating the trip."}), 500

# create a function called delete_trip, that takes in a user id and a trip id and deletes the trip associated with the user as well as all trip guests associated with the trip.
@trips_bp.route('/delete-trip', methods=['DELETE'])
@cross_origin()
@token_required
def delete_trip(token):

    data = get_request_data(token)
    app.logger.debug(data)
    # get params from request
    user_id = data['user_id']
    trip_id = data['trip_id']

    # Check if the user exists
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found."}), 404

    try:
        trip_id = int(trip_id)
    except ValueError as e:
        app.logger.error(e)
        return jsonify({"error": "Invalid trip ID."}), 400
    
    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404

    # Check if the user is the host of the trip
    if trip.host_id != user.id:
        return jsonify({"error": "User is not the host of this trip."}), 403

    try:
        # delete all trip guests
        TripGuest.query.filter_by(trip_id=trip_id).delete()
        # delete all expenses associated with the trip
        TripExpense.query.filter_by(trip_id=trip_id).delete()
        TripExpenseShare.query.filter_by(trip_id=trip_id).delete()

        # delete all locations
        TripLocation.query.filter_by(trip_id=trip_id).delete()
        LocationCategory.query.filter_by(trip_id=trip_id).delete()

        # delete itineraries
        ItineraryEntry.query.filter_by(trip_id=trip_id).delete()

        # delete todos
        TripTodo.query.filter_by(trip_id=trip_id).delete()
        uploads = UserUpload.query.filter_by(trip_id=trip_id).all()
        for upload in uploads:
            delete_trip_uploads(upload.file_name, trip_id)
            db.session.delete(upload)
        
        Trip.query.filter_by(id=trip_id).delete()

        db.session.commit()
        return jsonify({"message": "Trip deleted successfully."}), 200
    except Exception as e:
        app.logger.error(f"Error deleting trip: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the trip."}), 500

@trips_bp.route('/generate-invite', methods=['GET'])
@cross_origin()
@token_required
def generate_invite(token):
    data = get_request_data(token)
    app.logger.debug(data)
    trip_id = data['trip_id']

    try:
        trip_id = int(trip_id)
    except ValueError as e:
        app.logger.error(e)
        return jsonify({"error": "Invalid trip ID."}), 400

    # Generate an invite link
    invite_link = f"http://myapp.com/invite/{trip_id}"
    return jsonify({"invite_link": invite_link}), 200

@trips_bp.route('/add-todo', methods=['POST'])
@cross_origin()
@token_required
def add_todo(token):
    data = get_request_data(token)
    app.logger.debug(data)
    trip_id = data['trip_id']
    user_id = data['user_id']
    text = data['text']
    todo_id = data['id']

    try:
        trip_id = int(trip_id)
    except ValueError as e:
        app.logger.error(e)
        return jsonify({"error": "Invalid trip ID."}), 400
    
    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404
    
    # Check if the user is a guest of the trip and their rsvp status is YES
    trip_guest = TripGuest.query.filter_by(trip_id=trip_id, guest_id=user_id).first()
    if not trip_guest or trip_guest.rsvp_status != RsvpStatus.YES:
        return jsonify({"error": "User is not a guest of this trip."}), 403
    
    todo = TripTodo(id=todo_id, trip_id=trip_id, text=text, checked=False, last_updated_by=user_id, last_updated_at=datetime.now())
    
    try:
        db.session.add(todo)
        db.session.commit()
        return jsonify({"message": "Note added successfully."}), 200
    except Exception as e:
        app.logger.error(e)
        return jsonify({"error": "An error occurred while adding the note."}), 500

@trips_bp.route('/delete-todo', methods=['DELETE'])
@cross_origin()
@token_required
def delete_todo(token):
    data = get_request_data(token)
    app.logger.debug(data)
    user_id = data['user_id']
    todo_id = data['id']
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
    
    # Check if the user is the host of the trip and their rsvp status is YES
    trip_guest = TripGuest.query.filter_by(trip_id=trip_id, guest_id=user_id).first()
    if not trip_guest or not trip_guest.is_host:
        return jsonify({"error": "User is not the host of this trip."}), 403
    
    try:
        TripTodo.query.filter_by(id=todo_id, trip_id=trip_id).delete()
        db.session.commit()
        return jsonify({"message": "Note deleted successfully."}), 200
    except Exception as e:
        app.logger.error(f"Error deleting note from trip: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the note."}), 500

@trips_bp.route('/get-todos', methods=['GET', 'OPTIONS'])
@cross_origin()
@token_required
def get_todos(token):
    app.logger.info("trips/get-todos")
    
    data = get_request_data(token)
    app.logger.debug(data)
    trip_id = data['trip_id']
    user_id = data['user_id']
    
    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404
    
    # Check if the user is a guest of the trip
    trip_guest = TripGuest.query.filter_by(trip_id=trip_id, guest_id=user_id).first()
    if not trip_guest:
        return jsonify({"error": "User is not a guest of this trip."}), 403
    
    # Get all todos associated with the trip
    todos = TripTodo.query.filter_by(trip_id=trip_id).all()
    todo_list = []
    for todo in todos:
        todo_list.append({
            "id": todo.id,
            "text": todo.text,
            "checked": todo.checked
        })

    return jsonify({"todos": todo_list}), 200

@trips_bp.route('/update-todo', methods=['PUT'])
@cross_origin()
@token_required
def update_todo(token):
    app.logger.info("trips/update-todo")

    data = get_request_data(token)
    app.logger.debug(data)

    trip_id = data['trip_id']
    todo_id = data['id']
    text = data['text']
    checked = data['checked']
    user_id = data['user_id']

    try:
        trip_id = int(trip_id)
    except ValueError as e:
        app.logger.error(e)
        return jsonify({"error": "Invalid trip ID."}), 400

    # Check if the trip exists
    trip = Trip.query.filter_by(id=trip_id).first()
    if not trip:
        return jsonify({"error": "Trip not found."}), 404

    # Check if the user is a guest of the trip and their rsvp status is YES
    trip_guest = TripGuest.query.filter_by(trip_id=trip_id, guest_id=user_id).first()
    if not trip_guest or trip_guest.rsvp_status != RsvpStatus.YES:
        return jsonify({"error": "User is not a guest of this trip."}), 403

    todo = TripTodo.query.filter_by(id=todo_id, trip_id=trip_id).first()
    if not todo:
        return jsonify({"error": "Todo not found."}), 404

    try:
        todo.text = text
        todo.checked = checked
        todo.last_updated_by = user_id
        todo.last_updated_at = datetime.now()
        db.session.commit()
        return jsonify({"message": "Note updated successfully."}), 200
    except Exception as e:
        app.logger.error(e)
        return jsonify({"error": "An error occurred while updating the note."}), 500
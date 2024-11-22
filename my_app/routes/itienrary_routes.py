from datetime import datetime
from flask import Blueprint, jsonify, request
from flask import current_app as app
from flask_cors import cross_origin
from models import Trip, db, TripGuest, User, TripLocation, LocationCategory, ItineraryEntry
from .utils import token_required, get_request_data, validate_user_trip

itineraries_bp = Blueprint('trip_itinerary', __name__)

@itineraries_bp.route('/add-item', methods=['POST'])
@cross_origin()
@token_required
def add_item(token):
    app.logger.info("trip_itinerary/add-item")

    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    trip_id = data['trip_id']
    date = data['date']
    description = data['description']
    id = data['item_id']

    valid, error = validate_user_trip(user_id, trip_id)
    if not valid:
        return jsonify({"message": f"Invalid user or trip id: {error}"}), 400
    
    try:
        date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")
    except ValueError as e:
        app.logger.error(e)
        return jsonify({"message": "Invalid date format. Use 'Fri, 08 Nov 2024 00:00:00 GMT'."}), 400

    
    if description and description.strip() == "":
        return jsonify({"message": "Description cannot be empty."}), 400
    
    try:
        new_item = ItineraryEntry(trip_id=trip_id, date=date, description=description, id=id)
        db.session.add(new_item)
        db.session.commit()
    except Exception as e:
        app.logger.error(e)
        return jsonify({"message": "Error adding itinerary item."}), 500
    
    return jsonify({"message": "Itinerary item added successfully."}), 201

@itineraries_bp.route('/update-item', methods=['PUT'])
@cross_origin()
@token_required
def update_item(token):
    app.logger.info("trip_itinerary/update-item")

    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    trip_id = data['trip_id']
    date = data['date']
    description = data['description']
    id = data['item_id']

    valid, error = validate_user_trip(user_id, trip_id)
    if not valid:
        return jsonify({"message": f"Invalid user or trip id: {error}"}), 400
    
    try:
        date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")
    except ValueError as e:
        app.logger.error(e)
        return jsonify({"message": "Invalid date format. Use 'Fri, 08 Nov 2024 00:00:00 GMT'."}), 400
    
    if description and description.strip() == "":
        return jsonify({"message": "Description cannot be empty."}), 400
    
    item = ItineraryEntry.query.filter_by(id=id).first()
    if not item:
        return jsonify({"message": "Item not found."}), 404
    
    item.date = date
    item.description = description
    try:
        db.session.commit()
    except Exception as e:
        app.logger.error(e)
        return jsonify({"message": "Error updating itinerary item."}), 500
    
    return jsonify({"message": "Itinerary item updated successfully."}), 200
    
@itineraries_bp.route('/get-itinerary', methods=['GET'])
@cross_origin()
@token_required
def get_itinerary(token):
    app.logger.info("trip_itinerary/get-itinerary")

    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    trip_id = data['trip_id']

    valid, error = validate_user_trip(user_id, trip_id)
    if not valid:
        return jsonify({"message": f"Invalid user or trip id: {error}"}), 400
    
    # get the itinerary items for the trip
    itinerary = ItineraryEntry.query.filter_by(trip_id=trip_id).all()
    res = []
    for item in itinerary:
        res.append({
            "id": item.id,
            "date": item.date,
            "description": item.description,
        })
    return jsonify({"itinerary": res}), 200

@itineraries_bp.route('/delete-item', methods=['DELETE'])
@cross_origin()
@token_required
def delete_item(token):
    app.logger.info("trip_itinerary/delete-item")

    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    trip_id = data['trip_id']

    valid, error = validate_user_trip(user_id, trip_id)
    if not valid:
        return jsonify({"message": f"Invalid user or trip id: {error}"}), 400
    
    item_id = data['item_id']
    try:
        item_id = int(item_id)
    except ValueError as e:
        app.logger.error(e)
        return jsonify({"message": "Invalid item ID."}), 400
    
    item = ItineraryEntry.query.filter_by(id=item_id).first()
    if not item:
        return jsonify({"message": "Item not found."}), 404
    
    try:
        db.session.delete(item)
        db.session.commit()
    except Exception as e:
        app.logger.error(e)
        return jsonify({"message": "Error deleting itinerary item."}), 500
    
    return jsonify({"message": "Itinerary item deleted successfully."}), 200

from flask import Blueprint, jsonify, request
from flask import current_app as app
from flask_cors import cross_origin
from models import Trip, db, TripGuest, User, TripLocation, LocationCategory
from .utils import token_required, get_request_data, validate_user_trip

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
    place_name = data['place_name']
    place_id = data['place_id']
    category_name = data['category_name']

    valid, error = validate_user_trip(user_id, trip_id)
    if not valid:
        return jsonify({"message": f"Invalid user or trip id: {error}"}), 400
    
    # get the category id from the category name
    category_id = None
    if category_name:
        category = LocationCategory.query.filter_by(trip_id=trip_id, name=category_name).first()
        if not category:
            try:
                category = LocationCategory(trip_id=trip_id, name=category_name)
                db.session.add(category)
                db.session.commit()
                category_id = category.id
            except Exception as e:
                app.logger.error(f"Error adding category to location: {e}")
                db.session.rollback()
                return jsonify({"error": "An error occurred while adding the category to the DB."}), 500
        else:
            category_id = category.id

    try:
        # Add the location to the trip
        trip_location = TripLocation(trip_id=trip_id, user_id=user_id, latitude=lat, longitude=lng, name=place_name, place_id=place_id, category_id=category_id)
        db.session.add(trip_location)
        db.session.commit()

    except Exception as e:
        app.logger.error(f"Error adding location to trip: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while adding the user to the DB."}), 500

    return jsonify({"message": "Location successfully added."}), 201

@trip_locations_bp.route('/add-category', methods=['POST'])
@cross_origin()
@token_required
def add_category(token):
    app.logger.info("trip_locations/add-category")

    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    trip_id = data['trip_id']
    category = data['category']

    valid, error = validate_user_trip(user_id, trip_id)
    if not valid:
        return jsonify({"message": f"Invalid user or trip id: {error}"}), 400
    
    # check if the category already exists
    if LocationCategory.query.filter_by(trip_id=trip_id, name=category).first():
        return jsonify({"error": "Category already exists."}), 400

    try:
        # Add the category to the trip
        category = LocationCategory(trip_id=trip_id, name=category)
        db.session.add(category)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Error adding category to trip: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while adding the category to the DB."}), 500
    
    return jsonify({"message": "Category successfully added."}), 201

@trip_locations_bp.route('/get-locations', methods=['GET'])
@cross_origin()
@token_required
def get_locations(token):
    app.logger.info("trip_locations/get-locations")

    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    trip_id = data['trip_id']

    valid, error = validate_user_trip(user_id, trip_id)
    if not valid:
        return jsonify({"message": f"Invalid user or trip id: {error}"}), 400
    
    # Get all locations for the trip
    locations = TripLocation.query.filter_by(trip_id=trip_id).all()
    res = []
    for loc in locations:
        if not loc.category_id:
            category = None
        else:
            category = LocationCategory.query.filter_by(trip_id=trip_id, id=loc.category_id).first()
        res.append({"name": loc.name, "lat": loc.latitude, "lng": loc.longitude, "place_id": loc.place_id, "category": category.name if category else None, "category_id": loc.category_id})
    print(res)

    # get all the categories from the category table for the trip and add them to the response if they are not already in the response
    categories = LocationCategory.query.filter_by(trip_id=trip_id).all()
    for cat in categories:
        if cat.name not in [r['category'] for r in res]:
            res.append({"name": None, "lat": None, "lng": None, "place_id": None, "category": cat.name, "category_id": cat.id})

    return jsonify({"locations": res}), 200

@trip_locations_bp.route('/update-location', methods=['PUT'])
@cross_origin()
@token_required
def update_location(token):
    app.logger.info("trip_locations/update-location")

    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    trip_id = data['trip_id']
    place_name = data['place_name']
    place_id = data['place_id']
    category_name = data['category_name']

    valid, error = validate_user_trip(user_id, trip_id)
    if not valid:
        return jsonify({"message": f"Invalid user or trip id: {error}"}), 400
    
    # Get the location
    location = TripLocation.query.filter_by(place_id=place_id, trip_id=trip_id).first()
    if not location:
        return jsonify({"error": "Location not found."}), 404
    
    # Get the category
    category = LocationCategory.query.filter_by(trip_id=trip_id, name=category_name).first()
    if not category:
        return jsonify({"error": "Category not found."}), 404
    
    try:
        location.name = place_name
        location.category_id = category.id
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Error updating location: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the location."}), 500
    
    return jsonify({"message": "Location successfully updated."}), 200

@trip_locations_bp.route('/delete-location', methods=['DELETE'])
@cross_origin()
@token_required
def delete_location(token):
    app.logger.info("trip_locations/delete-location")

    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    trip_id = data['trip_id']
    place_id = data['place_id']

    valid, error = validate_user_trip(user_id, trip_id)
    if not valid:
        return jsonify({"message": f"Invalid user or trip id: {error}"}), 400
    
    # Get the location
    location = TripLocation.query.filter_by(place_id=place_id, trip_id=trip_id).first()
    if not location:
        return jsonify({"error": "Location not found."}), 404
    
    try:
        db.session.delete(location)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Error deleting location: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the location."}), 500
    
    return jsonify({"message": "Location successfully deleted."}), 200

@trip_locations_bp.route('/delete-category', methods=['DELETE'])
@cross_origin()
@token_required
def delete_category(token):
    app.logger.info("trip_locations/delete-category")

    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    trip_id = data['trip_id']

    valid, error = validate_user_trip(user_id, trip_id)
    if not valid:
        return jsonify({"message": f"Invalid user or trip id: {error}"}), 400
    
    category_name = data['category_name']
    category_id = None

    if not category_name:
        return jsonify({"error": "Category name is required."}), 400
    
    category = LocationCategory.query.filter_by(trip_id=trip_id, name=category_name).first()
    if not category:
        return jsonify({"error": "Category not found."}), 404
    category_id = category.id

    try:
        for location in TripLocation.query.filter_by(trip_id=trip_id, category_id=category_id).all():
            db.session.delete(location)
        db.session.delete(category)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Error deleting category: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the category."}), 500
    
    return jsonify({"message": "Category successfully deleted."}), 200

@trip_locations_bp.route('/update-category', methods=['PUT'])
@cross_origin()
@token_required
def update_category(token):
    app.logger.info("trip_locations/update-category")

    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    trip_id = data['trip_id']

    valid, error = validate_user_trip(user_id, trip_id)
    if not valid:
        return jsonify({"message": f"Invalid user or trip id: {error}"}), 400
    
    old_category_name = data['old_category_name']
    new_category_name = data['new_category_name']

    if not new_category_name or new_category_name.strip() == "" or new_category_name == "Unassigned":
        return jsonify({"error": "Invalid category name."}), 400
    
    category = LocationCategory.query.filter_by(trip_id=trip_id, name=old_category_name).first()
    if not category:
        return jsonify({"error": "Category not found."}), 404
    
    try:
        category.name = new_category_name
        db.session.flush()
        # update all the locations with the new category name
        for location in TripLocation.query.filter_by(trip_id=trip_id, category_id=category.id).all():
            location.category_id = category.id
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Error updating category: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the category."}), 500
    
    return jsonify({"message": "Category successfully updated."}), 200
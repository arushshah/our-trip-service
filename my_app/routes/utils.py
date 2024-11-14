from functools import wraps
from flask import request, jsonify
from functools import wraps
from flask import jsonify, request
from firebase_admin import auth
from flask import current_app as app

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({"error": "Token is missing."}), 401
        try:
            decoded_token = auth.verify_id_token(token)
        except Exception as e:
            app.logger.error(e)
            return jsonify({"message": "Token is invalid!", "error": str(e)}), 401
        return f(decoded_token, *args, **kwargs)
    return decorated

def get_request_data(token=None):
    if request.method == 'GET':
        tmp = request.args.to_dict()
        tmp['phone_number'] = token['phone_number']
        tmp['user_id'] = token['user_id']
        return tmp
    elif request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
        if request.get_json():
            if token:
                return {**request.get_json(), "phone_number": token['phone_number'], "user_id": token['user_id']}
            else:
                return request.get_json()
        return {}

def check_required_json_data(required_fields):
    data = request.json
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"})
    else:
        return True, None
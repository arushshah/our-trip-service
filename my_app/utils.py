from functools import wraps
from flask import jsonify, request
from firebase_admin import auth

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
            return jsonify({"message": "Token is invalid!", "error": str(e)}), 401
        return f(decoded_token, *args, **kwargs)
    return decorated
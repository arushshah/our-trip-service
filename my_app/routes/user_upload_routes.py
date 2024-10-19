from flask import Blueprint, jsonify, request
from my_app.models import User, UserUpload, db
import os
import boto3
from botocore.exceptions import NoCredentialsError

from my_app.models.trip import Trip

user_uploads_bp = Blueprint('uploads', __name__)
bucket_name = os.environ.get('S3_BUCKET_NAME')

@user_uploads_bp.route('/generate-presigned-url', methods=['POST'])
def generate_presigned_url():
    file_name = request.json.get('file_name')
    user_username = request.json.get('user_username')
    trip_id = request.json.get('trip_id')
    file_type = request.json.get('file_type')

    # convert trip id to int
    try:
        trip_id = int(trip_id)
    except ValueError:
        return jsonify({"error": "Invalid trip ID."}), 400

    if not file_name:
        return jsonify({"error": "File name is required."}), 400
    
    
    # Check if the user exists
    user = User.query.filter_by(username=user_username).first()
    if not user:
        return jsonify({"error": "User not found."}), 404
    
    # Check if the trip exists
    if trip_id:
        trip = Trip.query.filter_by(id=trip_id).first()
        if not trip:
            return jsonify({"error": "Trip not found."}), 404

    # Set an expiration time for the pre-signed URL
    expiration = 3600  # 1 hour
    
    try:
        s3_client = boto3.client('s3', region_name='us-east-1')
        url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': f"user_uploads/{trip_id}/{user_username}/{file_name}",
                'ContentType': file_type

            },
            ExpiresIn=expiration
        )
        return jsonify({"url": url}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Could not generate URL."}), 500
    
@user_uploads_bp.route('/save-upload-metadata', methods=['POST'])
def save_upload_metadata():
    data = request.json
    user_id = data['user_id']
    trip_id = data.get('trip_id')
    file_name = data['file_name']
    s3_url = data['s3_url']

    try:
        new_upload = UserUpload(
            user_id=user_id, trip_id=trip_id, file_name=file_name, s3_url=s3_url
        )
        db.session.add(new_upload)
        db.session.commit()
        return jsonify({"message": "Metadata saved successfully."}), 201
    except Exception as e:
        print(e)
        return jsonify({"error": "Could not save metadata."}), 500
    
@user_uploads_bp.route('/retrieve-uploads', methods=['GET'])
def retrieve_uploads():
    user_username = request.args.get('user_username')  # Get the username from query params

    if not user_username:
        return jsonify({"error": "User username is required."}), 400

    try:
        # List objects in the specified user's uploads directory
        prefix = f"user_uploads/{user_username}/"
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        if 'Contents' not in response:
            return jsonify({"message": "No files found."}), 404

        files = []
        for obj in response['Contents']:
            files.append({
                'file_name': obj['Key'],
                'last_modified': obj['LastModified'].isoformat(),
                'size': obj['Size']
            })

        return jsonify(files), 200

    except NoCredentialsError:
        return jsonify({"error": "Credentials not available."}), 500
    except Exception as e:
        print(e)
        return jsonify({"error": "Could not retrieve files."}), 500
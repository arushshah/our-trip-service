from flask import Blueprint, jsonify, request
from my_app.models import User, UserUpload, db
import os
import boto3
from botocore.exceptions import NoCredentialsError
import my_app.validation as validator
from my_app.utils import token_required
from my_app.models.trip import Trip

user_uploads_bp = Blueprint('uploads', __name__)
bucket_name = os.environ.get('S3_BUCKET_NAME')

@user_uploads_bp.route('/generate-presigned-url', methods=['POST'])
@token_required
def generate_presigned_url(token):

    file_name = request.json.get('file_name')
    user_id = token['phone_number']
    document_category = request.json.get('document_category')
    trip_id = request.json.get('trip_id')
    file_type = request.json.get('file_type')
    url_type = request.json.get('url_type') # should be either upload or download

    try:
        trip_id = int(trip_id)
    except ValueError:
        return jsonify({"error": "Invalid trip ID."}), 400

    if not file_name:
        return jsonify({"error": "File name is required."}), 400
    
    res = validator.validate_user_id(user_id)
    if res != "valid":
        return res
        
    # validate document category
    if not document_category:
        return jsonify({"error": "Document category is required."}), 400
    
    if document_category not in ["travel", "accommodation"]:
        return jsonify({"error": "Invalid document category."}), 400
        
    expiration = 300
    s3_client = boto3.client('s3', region_name='us-east-1')
    s3_key = f"user_uploads/{document_category}/{trip_id}/{file_name}"
    print(s3_key)

    if url_type == "download":
        try:
            download_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            print(download_url)
            return jsonify({"download_url": download_url}), 200
        except NoCredentialsError:
            return jsonify({"error": "Credentials not available."}), 403
        except Exception as e:
            print(e)
            return jsonify({"error": "Could not generate URLs."}), 500

    else:
        try:
            url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': s3_key,
                    'ContentType': file_type
                },
                ExpiresIn=expiration
            )
            save_upload_metadata(user_id, trip_id, file_name, s3_key, document_category)
            return jsonify({"url": url}), 200
        except Exception as e:
            print(e)
            return jsonify({"error": "Could not generate URL."}), 500
    
def save_upload_metadata(user_id, trip_id, file_name, s3_key, document_category):

    try:
        if not UserUpload.query.filter_by(trip_id=trip_id, file_name=file_name).first():
            new_upload = UserUpload(
                user_id=user_id, trip_id=trip_id, document_category=document_category, file_name=file_name, s3_url=s3_key
            )
            db.session.add(new_upload)
            db.session.commit()
    except Exception as e:
        print(e)
        print("error: Could not save metadata.")
    
@user_uploads_bp.route('/retrieve-trip-uploads', methods=['GET'])
@token_required
def retrieve_uploads(token):
    # query the user_upload table for all uploads associated with a trip
    trip_id = request.args.get('trip_id')
    document_category = request.args.get('document_category')

    try:
        trip_id = int(trip_id)
    except ValueError:
        return jsonify({"error": "Invalid trip ID."}), 400
    
    # validate document category
    if not document_category:
        return jsonify({"error": "Document category is required."}), 400
    
    if document_category not in ["travel", "accommodation"]:
        return jsonify({"error": "Invalid document category."}), 400
    
    uploads = UserUpload.query.filter_by(trip_id=trip_id, document_category=document_category).all()
    upload_list = []
    for upload in uploads:
        upload_list.append({
            "file_name": upload.file_name,
            "s3_url": upload.s3_url
        })

    return jsonify({"uploads": upload_list}), 200

@user_uploads_bp.route('/delete-upload', methods=['POST'])
@token_required
def delete_upload(token):
    file_name = request.json.get('file_name')
    trip_id = request.json.get('trip_id')
    return delete_trip_uploads(file_name, trip_id)

def delete_trip_uploads(file_name, trip_id):
    try:
        trip_id = int(trip_id)
    except ValueError:
        return jsonify({"error": "Invalid trip ID."}), 400

    if not file_name:
        return jsonify({"error": "File name is required."}), 400

    upload = UserUpload.query.filter_by(trip_id=trip_id, file_name=file_name).first()
    if not upload:
        return jsonify({"error": "Upload not found."}), 404

    s3_key = upload.s3_url
    s3_client = boto3.client('s3', region_name='us-east-1')

    try:
        s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
        db.session.delete(upload)
        db.session.commit()
        return jsonify({"message": "Upload deleted successfully."}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Could not delete upload."}), 500

            
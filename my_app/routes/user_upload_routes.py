from flask import Blueprint, jsonify, request, current_app as app
from flask_cors import cross_origin
from models import UserUpload, db, DocumentCategory
import os
import boto3
from botocore.exceptions import NoCredentialsError
from .utils import get_request_data, token_required

user_uploads_bp = Blueprint('uploads', __name__)

bucket_name = os.environ.get('S3_BUCKET_NAME')

@user_uploads_bp.route('/generate-presigned-url', methods=['POST'])
@cross_origin()
@token_required
def generate_presigned_url(token):

    app.logger.info("uploads/generate-presigned-url")
    data = get_request_data(token)
    app.logger.debug(data)

    file_name = data['file_name']
    user_id = data['user_id']
    document_category = data['document_category']
    trip_id = data['trip_id']
    if 'file_type' in data:
        file_type = data['file_type']
    url_type = data['url_type'] # should be either upload or download

    try:
        trip_id = int(trip_id)
    except ValueError as e:
        app.logger.error(e)
        return jsonify({"error": "Invalid trip ID."}), 400

    if not file_name:
        return jsonify({"error": "File name is required."}), 400
        
    # validate document category
    if not document_category:
        return jsonify({"error": "Document category is required."}), 400
    
    try:
        document_category = DocumentCategory(document_category)
    except ValueError as e:
        app.logger.error(e)
        return jsonify({"error": "Invalid document category."}), 400
        
    expiration = 300
    s3_client = boto3.client('s3', region_name='us-east-1')
    s3_key = f"user_uploads/{document_category.value}/{trip_id}/{user_id}/{file_name}"

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
            return jsonify({"download_url": download_url}), 200
        except NoCredentialsError as e:
            app.logger.error(e)
            return jsonify({"error": "Credentials not available."}), 403
        except Exception as e:
            app.logger.error(e)
            return jsonify({"error": "Could not generate URLs."}), 500

    else:
        try:
            app.logger.debug(f"{bucket_name}, {s3_key}, {file_type}, {expiration}")
            url = s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': s3_key,
                    'ContentType': file_type
                },
                ExpiresIn=expiration
            )
            app.logger.debug("URL: ", url)
            save_upload_metadata(user_id, trip_id, file_name, s3_key, document_category)
            return jsonify({"url": url}), 200
        except Exception as e:
            app.logger.error(e)
            return jsonify({"error": "Could not generate URL."}), 500
    
def save_upload_metadata(user_id, trip_id, file_name, s3_key, document_category):
    app.logger.debug(f"user_id: {user_id}, trip_id: {trip_id}, file_name: {file_name}, s3_key: {s3_key}, doc_category: {document_category}")
    try:
        if not UserUpload.query.filter_by(s3_url=s3_key).first():
            new_upload = UserUpload(
                upload_user_id=user_id, trip_id=trip_id, document_category=document_category, file_name=file_name, s3_url=s3_key
            )
            db.session.add(new_upload)
            db.session.commit()
    except Exception as e:
        app.logger.error(e)
        print("Error saving upload metadata")
    
@user_uploads_bp.route('/retrieve-trip-uploads', methods=['GET'])
@cross_origin()
@token_required
def retrieve_uploads(token):
    data = get_request_data(token)
    app.logger.debug(data)
    # query the user_upload table for all uploads associated with a trip
    trip_id = data['trip_id']
    document_category = data['document_category']

    try:
        trip_id = int(trip_id)
    except ValueError as e:
        app.logger.error(e)
        return jsonify({"error": "Invalid trip ID."}), 400
    
    # validate document category
    if not document_category:
        return jsonify({"error": "Document category is required."}), 400
    
    try:
        document_category = DocumentCategory(document_category)
    except ValueError as e:
        app.logger.error(e)
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
@cross_origin()
@token_required
def delete_upload(token):
    app.logger.debug(data)
    data = get_request_data(token)
    file_name = data['file_name']
    trip_id = data['trip_id']
    return delete_trip_uploads(file_name, trip_id)

def delete_trip_uploads(file_name, trip_id):
    try:
        trip_id = int(trip_id)
    except ValueError as e:
        app.logger.error(e)
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
        app.logger.error(e)
        return jsonify({"error": "Could not delete upload."}), 500

            
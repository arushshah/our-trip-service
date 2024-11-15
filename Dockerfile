# Use Python 3.12 as the base image
FROM python:3.12-slim

# Prevent Python from writing bytecode files
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /our-trip-service

# Copy only requirements.txt first to leverage Docker layer caching
COPY requirements.txt /our-trip-service/

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire current directory (from your local machine) into /our-trip-service in the container
COPY . /our-trip-service

# Expose port 5555 (if Flask is running on this port)
EXPOSE 5555

# Set Flask environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
#ENV DB_URL=sqlite:///dev.db
ENV DB_URL=mysql://admin:K!ck3d^2011@our-trip-db.crkw0o28wjis.us-east-1.rds.amazonaws.com:3306/our_trip_db
ENV S3_BUCKET_NAME=our-trip-bucket

WORKDIR /our-trip-service/my_app

# Start the application
CMD ["gunicorn", "app:create_app()", "--bind", "0.0.0.0:5555"]

#!/bin/bash

# Set variables
IMAGE_NAME="our-trip-service"
ECR_REPOSITORY="043309356556.dkr.ecr.us-east-1.amazonaws.com/our-trip"
ECR_TAG="$ECR_REPOSITORY:$IMAGE_NAME"
REGION="us-east-1"

# Build the Docker image
echo "Building Docker image..."
docker buildx build --platform linux/amd64 -t $IMAGE_NAME .

# Tag the Docker image for ECR
echo "Tagging Docker image for ECR..."
docker tag $IMAGE_NAME:latest $ECR_TAG

# Authenticate Docker with ECR
echo "Authenticating Docker with ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REPOSITORY

# Push the Docker image to ECR
echo "Pushing Docker image to ECR..."
docker push $ECR_TAG

echo "Docker image successfully pushed to ECR."

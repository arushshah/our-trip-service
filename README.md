LOG INTO EC2
ssh -i OurTripKP.pem ec2-user@ec2-54-210-183-107.compute-1.amazonaws.com

RUN DOCKER CONTAINER LOCALLY

docker run -v ~/.aws:/root/.aws -p 5555:5555 our-trip-service

BUILD AND DEPLOY
./build.sh
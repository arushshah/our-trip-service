TO CREATE INFRA:
RUN THE FOLLOWING

awslocal cloudformation create-stack --stack-name our-trip-stack --template-body file://aws-infra/main.yaml

TO DELETE INFRA:
RUN THE FOLLOWING

awslocal cloudformation delete-stack --stack-name our-trip-stack

ENDPOINTS

/create-trip

https://ypfb2xz8ci.execute-api.us-east-1.amazonaws.com/dev/create-trip

CONNECTING TO EC2:
ssh -i OurTripKP.pem ec2-user@ec2-3-86-69-1.compute-1.amazonaws.com

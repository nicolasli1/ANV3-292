FROM python:3.9-slim

RUN apt-get update

RUN apt-get install -y nano htop curl

RUN pip install pandas==1.3.1

RUN pip install boto3

RUN curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

RUN npm install -g aws-cdk

CMD ["bash"]

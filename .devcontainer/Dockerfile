FROM python:3.9-slim

RUN apt-get update

RUN apt-get install -y nano htop curl git wget unzip

RUN pip install pandas==1.3.1

RUN curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

RUN pip install aws-sam-cli

WORKDIR /workspace

CMD ["bash"]

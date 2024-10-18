FROM python:3.9-slim

RUN apt-get update

RUN apt-get install -y nano htop curl git wget unzip

RUN pip install pandas==1.3.1

RUN pip install aws-cdk-lib>=2.0.0 constructs>=10.0.0 boto3==1.34.125 black

RUN curl -sL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Instala Terraform
RUN wget https://releases.hashicorp.com/terraform/1.9.5/terraform_1.9.5_linux_amd64.zip \
    && unzip terraform_1.9.5_linux_amd64.zip \
    && mv terraform /usr/local/bin/ 


RUN npm install -g aws-cdk

WORKDIR /workspace

CMD ["bash"]

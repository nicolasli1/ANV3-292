#!/bin/bash
sudo yum update -y
sudo yum install -y httpd
sudo systemctl start httpd
sudo systemctl enable httpd
sudo echo "<html><body><h1>Welcome to ${project_name} Apache httpd web server!</h1></body></html>" > /var/www/html/index.html
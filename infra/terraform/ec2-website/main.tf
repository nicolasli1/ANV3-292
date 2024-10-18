# crear una vpc 

resource "aws_vpc" "my-vpc-292" {
  cidr_block = "10.0.0.0/16"
}

# crear subnedes de mi vpc

resource "aws_subnet" "subnet-1" {
  vpc_id                  = aws_vpc.my-vpc-292.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
  tags = {
    Name = "${var.ec2-taller1}-subnet-1"
  }
}

# crear internetgateway 

resource "aws_internet_gateway" "my-vpc-292-ig" {
  vpc_id = aws_vpc.my-vpc-292.id
  tags = {
    Name = "${var.ec2-taller1}-ig"
  }
}

#creacion de la route table 

resource "aws_route_table" "my-vpc-292-rt" {
  vpc_id = aws_vpc.my-vpc-292.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.my-vpc-292-ig.id
  }
  tags = {
    Name = "${var.ec2-taller1}-route-table"
  }
}

resource "aws_route_table_association" "awsrta-1" {
  subnet_id      = aws_subnet.subnet-1.id
  route_table_id = aws_route_table.my-vpc-292-rt.id
}

#crear el security group
resource "aws_security_group" "allow-trafic" {
  name        = "allow-trafict-name"
  description = "Permitir el trafico de internet a ssh y al puerto 80"
  vpc_id      = aws_vpc.my-vpc-292.id

  ingress {
    description = "Trafico HTTP a VPC"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Trafico SSH a VPC"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "${var.ec2-taller1}-allow-trafic"
  }
}

#crear la configuracion de nuestro launch 

resource "aws_launch_configuration" "lc" {
  name            = "${var.ec2-taller1}-lc"
  image_id        = "ami-06b21ccaeff8cd686"
  instance_type   = "t2.micro"
  security_groups = [aws_security_group.allow-trafic.id]
  key_name        = "Nicolas-key"
  user_data       = file("apache_httpd.sh")

}

resource "aws_autoscaling_group" "asg" {
  name                 = "${var.ec2-taller1}-ag"
  desired_capacity     = 4
  max_size             = 10
  min_size             = 2
  health_check_type    = "EC2"
  vpc_zone_identifier  = [aws_subnet.subnet-1.id]
  launch_configuration = aws_launch_configuration.lc.name
}

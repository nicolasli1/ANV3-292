from os import path # Se utiliza para manejar rutas de archivos
import os.path 
import aws_cdk as cdk

from constructs import Construct # Se utiliza como clase base para los constructores de CDK

from aws_cdk import(
    aws_ec2 as ec2,
    aws_iam as iam,
    App,
    Stack
)

class Ec2VpcStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs) #Constructor clase

        vpc = ec2.Vpc(
            self,
            id="MyVpcTalle1",
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name="PublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC
                ),
            ]
        )
        
        # AMI
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
            )
            
        # Instance Role and SSM Managed Policy
        role = iam.Role(self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "sudo yum update -y",
            "sudo yum install -y httpd",
            "sudo systemctl start httpd",
            "sudo systemctl enable httpd",
            "sudo echo 'Hola Mundo!' > /var/www/html/index.html"
        )

        # Instance
        instance = ec2.Instance(self, "Instance",
            instance_type=ec2.InstanceType("t2.micro"),
            vpc = vpc,
            machine_image=amzn_linux,
            role=role,
            user_data=user_data
            )
        instance.connections.allow_from(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80)
        )
        instance.connections.allow_from(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(22)
        )
app = App()
Ec2VpcStack(app, "ec2-instance")
app.synth()

from os import path
import os.path
import aws_cdk as cdk

from constructs import Construct

from aws_cdk import(
    aws_ec2 as ec2,
    App,
    Stack
)

class Ec2VpcStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(
            self,
            id="MyVpcClass",
            max_azs=3,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                   cidr_mask=24,
                   name="PublicSubnet",
                   subnet_type=ec2.SubnetType.PUBLIC
               ),
            ]
        )
app = App()
Ec2VpcStack(app, "vpc")

app.synth()
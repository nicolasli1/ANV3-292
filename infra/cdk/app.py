from os import path
import os.path
import aws_cdk as cdk

from constructs import Construct
from aws_cdk import Duration, RemovalPolicy
from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_apigateway as api_g,
    aws_lambda as lb,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    App,
    Stack,
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
                    cidr_mask=24, name="PublicSubnet", subnet_type=ec2.SubnetType.PUBLIC
                ),
            ],
        )

        # AMI
        # Se selecciona la ultima version de Amazon Linux 2
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
        )

        role = iam.Role(
            self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
        )
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"
            )
        )

        user_data = ec2.UserData.for_linux()

        user_data.add_commands(
            "sudo yum update -y",
            "sudo yum install -y httpd",
            "sudo systemctl start httpd",
            "sudo systemctl enable httpd",
            "sudo echo 'Hola Mundo!' > /var/www/html/index.html",
        )

        instance = ec2.Instance(
            self,
            "Instance",
            instance_type=ec2.InstanceType("t2.micro"),
            vpc=vpc,
            machine_image=amzn_linux,
            role=role,
            user_data=user_data,
        )

        instance.connections.allow_from(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))

        instance.connections.allow_from(ec2.Peer.any_ipv4(), ec2.Port.tcp(22))


class MiPrimerAPI(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        fn_get_menu = lb.Function(
            self,
            id="Fn_get_menu_id",
            handler="lambda_get_menu_code.lambda_handler",
            code=lb.Code.from_asset("../../lambda/Fn_get_menu_code"),
            timeout=Duration.seconds(2),
            runtime=lb.Runtime.PYTHON_3_12,
        )

        fn_get_items_table = lb.Function(
            self,
            id="Fn_get_items_table",
            handler="lambda_get_items_code.lambda_handler",
            code=lb.Code.from_asset("../../lambda/Fn_get_menu_code"),
            timeout=Duration.seconds(60),
            runtime=lb.Runtime.PYTHON_3_12,
        )

        global_table = dynamodb.TableV2(
            self,
            id="GlobalTable",
            table_name="My_primera_global_table_292",
            billing=dynamodb.Billing.on_demand(),
            partition_key=dynamodb.Attribute(
                name="id_pk", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        global_table.grant_full_access(fn_get_items_table)

        api_1 = api_g.RestApi(self, id="Class-229", rest_api_name="Api-Anv3-292")

        menu_resource = api_1.root.add_resource("menu")
        items_table = api_1.root.add_resource("items")

        integration_fn_get_menu = api_g.LambdaIntegration(fn_get_menu)
        integration_fn_get_items = api_g.LambdaIntegration(fn_get_items_table)

        menu_resource.add_method(
            "GET",
            integration_fn_get_menu,
        )

        items_table.add_method(
            "GET",
            integration_fn_get_items,
        )


class MyWebsiteS3(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bucket = s3.Bucket(
            self,
            id="Bucker-292",
            public_read_access=True,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
                block_public_policy=False,
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )



app = App()
Ec2VpcStack(app, "vpc")
MiPrimerAPI(app, "mi-api")
MyWebsiteS3(app, "my-website-s3")

app.synth()

import base64
from os import path
import os.path
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import Duration
from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_apigateway as api_g,
    aws_lambda as lb,
    aws_dynamodb as dynamodb,
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
        # Read and encode the local HTML file content
        html_file_path = '../../WebSite/index.html'
         
        with open(html_file_path, 'r') as file:
            file_content = file.read()

        # Encode the file content in base64 to handle multi-line content
        encoded_content = base64.b64encode(file_content.encode("utf-8")).decode("utf-8")

        user_data.add_commands(
            "sudo yum update -y",
            "sudo yum install -y httpd",
            "sudo systemctl start httpd",
            "sudo systemctl enable httpd",
           # Decode base64 content and write it to index.html
            f"echo {encoded_content} | base64 -d | sudo tee /var/www/html/index.html > /dev/null"
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
        instance.connections.allow_from_any_ipv4(ec2.Port.tcp(80), "Allow HTTP")

        #instance.connections.allow_from(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))

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

        fn_post_order = lb.Function(
            self,
            id="Fn_post_order",
            handler="lambda_post_order.lambda_handler",
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
        global_table.grant_write_data(fn_post_order)
        api_1 = api_g.RestApi(self, id="Class-229", 
                              rest_api_name="Api-Anv3-292",  
                              default_cors_preflight_options=api_g.CorsOptions(
                                    allow_headers=['Content-Type'],
                                    allow_origins=api_g.Cors.ALL_ORIGINS,
                                    allow_methods=api_g.Cors.ALL_METHODS,
                               )
        ) 
                         
        menu_resource = api_1.root.add_resource("menu")
        items_table = api_1.root.add_resource("items")
        order_resource = api_1.root.add_resource("save_order")

        integration_fn_get_menu = api_g.LambdaIntegration(fn_get_menu)
        integration_fn_get_items = api_g.LambdaIntegration(fn_get_items_table)
        integration_fn_post_order = api_g.LambdaIntegration(fn_post_order)

        menu_resource.add_method(
            "GET",
            integration_fn_get_menu,
        )

        items_table.add_method(
            "GET",
            integration_fn_get_items,
        )
        
        order_resource.add_method(
            "POST",
            integration_fn_post_order,
        )

app = App()
Ec2VpcStack(app, "vpc")
MiPrimerAPI(app, "mi-api")

app.synth()

from os import path
import os.path
import aws_cdk as cdk

from constructs import Construct
from aws_cdk import Duration
from aws_cdk import (
    aws_ec2 as ec2,
    aws_apigateway as api_g,
    aws_lambda as lb,
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

        api_1 = api_g.RestApi(self, id="Class-229", rest_api_name="Api-Anv3-292")

        menu_resource = api_1.root.add_resource("menu")

        integration_fn_get_menu = api_g.LambdaIntegration(fn_get_menu)

        menu_resource.add_method(
            "GET",
            integration_fn_get_menu,
        )


app = App()
Ec2VpcStack(app, "vpc")
MiPrimerAPI(app, "mi-api")

app.synth()

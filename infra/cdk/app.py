from os import path
import os.path

import aws_cdk as cdk



from constructs import Construct
from aws_cdk import Duration, RemovalPolicy
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_ecs_patterns as ecs_patterns
import aws_cdk.aws_stepfunctions_tasks as tasks
from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_apigateway as api_g,
    aws_lambda as lb,
    aws_dynamodb as dynamodb,
    aws_cloudfront as cf,
    aws_cloudfront_origins as origins,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_ecs as ecs,
    aws_logs as logs,
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
            code=lb.Code.from_asset("../../lambda/menu_code"),
            timeout=Duration.seconds(2),
            runtime=lb.Runtime.PYTHON_3_12,
        )

        fn_get_items_table = lb.Function(
            self,
            id="Fn_get_items_table",
            handler="lambda_get_items_code.lambda_handler",
            code=lb.Code.from_asset("../../lambda/menu_code"),
            timeout=Duration.seconds(20),
            runtime=lb.Runtime.PYTHON_3_12,
        )

        fn_post_items_table = lb.Function(
            self,
            id="Fn_post_items_table",
            handler="lambda_post_items_code.lambda_handler",
            code=lb.Code.from_asset("../../lambda/menu_code"),
            timeout=Duration.seconds(20),
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
        global_table.grant_full_access(fn_post_items_table)

        api_1 = api_g.RestApi(self, id="Class-229", rest_api_name="Api-Anv3-292")

        menu_resource = api_1.root.add_resource("menu")
        items_table = api_1.root.add_resource("items")

        integration_fn_get_menu = api_g.LambdaIntegration(fn_get_menu)
        integration_fn_get_items = api_g.LambdaIntegration(fn_get_items_table)
        integration_fn_post_items = api_g.LambdaIntegration(fn_post_items_table)

        menu_resource.add_method("GET", integration_fn_get_menu)
        items_table.add_method("GET", integration_fn_get_items)
        items_table.add_method("POST", integration_fn_post_items)

        items_table.add_method(
            "OPTIONS",
            api_g.MockIntegration(
                passthrough_behavior=api_g.PassthroughBehavior.NEVER,
                request_templates={"application/json": '{"statusCode": 200}'},
                integration_responses=[
                    api_g.IntegrationResponse(
                        status_code="200",
                        response_parameters={
                            "method.response.header.Access-Control-Allow-Origin": "'*'",
                            "method.response.header.Access-Control-Allow-Methods": "'GET, POST, PUT, OPTIONS'",
                            "method.response.header.Access-Control-Allow-Headers": "'Content-Type'",
                        },
                    )
                ],
            ),
            method_responses=[
                api_g.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True,
                        "method.response.header.Access-Control-Allow-Methods": True,
                        "method.response.header.Access-Control-Allow-Headers": True,
                    },
                )
            ],
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

        s3_deployment.BucketDeployment(
            self,
            id="DeploymentS3",
            sources=[s3_deployment.Source.asset("../../web/")],
            destination_bucket=bucket,
        )

        distribution = cf.CloudFrontWebDistribution(
            self,
            id="MyDistribution-292",
            origin_configs=[
                cf.SourceConfiguration(
                    s3_origin_source=cf.S3OriginConfig(s3_bucket_source=bucket),
                    behaviors=[cf.Behavior(is_default_behavior=True)],
                )
            ],
            error_configurations=[
                cf.CfnDistribution.CustomErrorResponseProperty(
                    error_code=404, response_code=404, response_page_path="/404.html"
                ),
                cf.CfnDistribution.CustomErrorResponseProperty(
                    error_code=403, response_code=403, response_page_path="/404.html"
                ),
            ],
        )


class ecsCluster(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Crear una VPC
        vpc = ec2.Vpc(self, "MyVpc", max_azs=2)


        security_group = ec2.SecurityGroup(self, "ecs-fargte",
            vpc=vpc,
            description="Allow HTTP traffic on port 80",
            allow_all_outbound=True  # Permitir todas las salidas
        )
        # Agregar una regla para permitir tráfico HTTP en el puerto 80 desde cualquier IP
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),  # Acepta tráfico desde cualquier IP (0.0.0.0/0)
            ec2.Port.tcp(80),  # Permitir tráfico en el puerto TCP 80 (HTTP)
            "Allow HTTP traffic"
        )

        # Crear un cluster ECS
        cluster = ecs.Cluster(self, "EcsCluster", vpc=vpc)

        # Crear la definición de la tarea ECS
        task_definition = ecs.FargateTaskDefinition(self, "TaskDef",
            memory_limit_mib=512,  # 512 MB
            cpu=256,  # 0.25 vCPU
        )

        # Agregar un contenedor a la definición de tarea
        container = task_definition.add_container("AppContainer",
            image=ecs.ContainerImage.from_registry("fermec28/express-app:latest"),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="myapp", log_retention=logs.RetentionDays.ONE_WEEK),
            #port_mappings=[ecs.PortMapping(container_port=3000)],
            environment={"PORT":"80"},
        )

        # Crear el servicio ECS
        ecs.FargateService(self, "FargateService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1,  # Número de instancias del contenedor a ejecutar
            assign_public_ip=True,  # Asigna una IP pública para poder acceder desde Internet
            security_groups=[security_group]
        )

app = App()
Ec2VpcStack(app, "vpc")
MiPrimerAPI(app, "mi-api")
MyWebsiteS3(app, "my-website-s3")
ecsCluster(app, "ecs-fargate")

app.synth()

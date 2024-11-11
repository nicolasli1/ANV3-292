# Estas líneas importan varios módulos y bibliotecas de Python.
# El módulo aws_cdk es el AWS Cloud Development Kit, que permite definir infraestructura en la nube utilizando Python.
# 
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
    Stack,
)
# Un stack en AWS CDK es una colección de recursos de AWS que puedes desplegar juntos.
class Ec2VpcStack(Stack):
    # inicializa la clase base (Stack).
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Se crea una VPC (Nube Virtual Privada) con el ID MyVpcClass.
        # La VPC tendrá hasta 3 zonas de disponibilidad (max_azs=3), sin NAT Gateways, y una configuración de subred pública.
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
        # Esto configura una AMI de Amazon Linux 2 (Imagen de Máquina de Amazon), 
        # que es el sistema operativo que se utilizará para la instancia EC2. 
        # Se selecciona la ultima version de Amazon Linux 2
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
        )

        # Esto crea un Rol IAM para la instancia EC2, con el nombre InstanceSSM.
        # El rol es asumido por el servicio EC2 (ec2.amazonaws.com), lo que le permite realizar ciertas acciones.
        role = iam.Role(
            self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
        )
        # Se le asigna la política gestionada AmazonSSMManagedInstanceCore, 
        # que es necesaria para que las instancias EC2 trabajen con AWS Systems Manager (SSM).
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"
            )
        )

        # Esto define los datos de usuario para la instancia EC2, que es un script que se ejecuta cuando la instancia se inicia.
        user_data = ec2.UserData.for_linux()
        # Read and encode the local HTML file content
        # Lee un archivo HTML (index.html) desde una ruta local y 
        # lo codifica en base64 para evitar problemas con caracteres especiales o saltos de línea.
        html_file_path = "../../WebSite/index.html"

        with open(html_file_path, "r") as file:
            file_content = file.read()

        # Encode the file content in base64 to handle multi-line content
        encoded_content = base64.b64encode(file_content.encode("utf-8")).decode("utf-8")

        # Los comandos de datos de usuario se ejecutarán cuando se inicie la instancia EC2:
        # Actualiza el sistema (yum update),
        # Instala el servidor HTTP Apache (httpd),
        # Inicia el servicio HTTP y lo habilita para que se ejecute al iniciar.
        # El contenido codificado en base64 se escribe en el directorio web predeterminado (/var/www/html/index.html).
        user_data.add_commands(
            "sudo yum update -y",
            "sudo yum install -y httpd",
            "sudo systemctl start httpd",
            "sudo systemctl enable httpd",
            # Decode base64 content and write it to index.html
            f"echo {encoded_content} | base64 -d | sudo tee /var/www/html/index.html > /dev/null",
        )
        # se crea una instancia EC2 utilizando la configuración especificada (tipo de instancia, VPC, AMI, rol IAM y datos de usuario).
        instance = ec2.Instance(
            self,
            "Instance",
            instance_type=ec2.InstanceType("t2.micro"),
            vpc=vpc,
            machine_image=amzn_linux,
            role=role,
            user_data=user_data,
        )
        # Esto permite el tráfico HTTP (puerto 80) desde cualquier dirección IPv4 para acceder a la instancia EC2, y 
        # también permite el acceso SSH (puerto 22) para la administración remota.
        instance.connections.allow_from_any_ipv4(ec2.Port.tcp(80), "Allow HTTP")
        # instance.connections.allow_from(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))
        instance.connections.allow_from(ec2.Peer.any_ipv4(), ec2.Port.tcp(22))


class MiPrimerAPI(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        #   Esto crea una función Lambda llamada Fn_get_menu_id, que usa el entorno de ejecución Python 3.12.
        # La función se encuentra en el directorio ../../lambda/Fn_get_menu_code y
        # será invocada por el manejador lambda_get_menu_code.lambda_handler.

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

        # Se crea una tabla DynamoDB con el nombre My_primera_global_table_292. 
        # La tabla utiliza el atributo id_pk como clave de partición.
        # La facturación de la tabla está configurada como a demanda (se cobra según el uso).
        # La política de eliminación se establece como DESTROY, lo que significa que la tabla será eliminada cuando el stack se destruya.

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

        # Estas dos líneas otorgan acceso total a la tabla DynamoDB (global_table) para dos funciones Lambda: fn_get_items_table y fn_post_order. 
        # Esto permite que las funciones Lambda lean, escriban y realicen cualquier otra operación en la tabla DynamoDB.

        global_table.grant_full_access(fn_get_items_table)
        global_table.grant_full_access(fn_post_order)

        # Esto crea una API Gateway REST API con el ID Class-229 y el nombre Api-Anv3-292. 
        # API Gateway se utiliza para exponer puntos de enlace HTTP que activan las funciones Lambda cuando se llaman.
        api_1 = api_g.RestApi(self,id="Class-229", rest_api_name="Api-Anv3-292")
           # default_cors_preflight_options=api_g.CorsOptions(
            #   allow_methods=["GET", "POST"], allow_origins=api_g.Cors.ALL_ORIGINS
            #),
    
        # Estas líneas definen tres recursos dentro de la API:
        # Un recurso para el endpoint menu (menu_resource),
        # Un recurso para el endpoint items (items_table),
        # Un recurso para el endpoint save_order (order_resource).
        # Estos son los caminos (URLs) en la API que los usuarios accederán para utilizar diferentes servicios.
        menu_resource = api_1.root.add_resource("menu")
        items_table = api_1.root.add_resource("items")
        order_resource = api_1.root.add_resource("save_order")

        # Estas líneas configuran las integraciones de Lambda para cada uno de los recursos de la API. 
        # Cuando un usuario accede a estos recursos (puntos finales), se activará la función Lambda correspondiente:
        # integration_fn_get_menu activa la función Lambda fn_get_menu,
        # integration_fn_get_items activa la función Lambda fn_get_items_table,
        # integration_fn_post_order activa la función Lambda fn_post_order.
        integration_fn_get_menu = api_g.LambdaIntegration(fn_get_menu)
        integration_fn_get_items = api_g.LambdaIntegration(fn_get_items_table)
        integration_fn_post_order = api_g.LambdaIntegration(fn_post_order)

        # Estas líneas definen los métodos HTTP para cada recurso de la API:
        # El menu_resource aceptará solicitudes GET y activará la función Lambda fn_get_menu.
        # El items_table aceptará solicitudes GET y activará la función Lambda fn_get_items_table.
        # El order_resource aceptará solicitudes POST y activará la función Lambda fn_post_order.
        menu_resource.add_method("GET", integration_fn_get_menu)
        items_table.add_method("GET", integration_fn_get_items)
        order_resource.add_method("POST", integration_fn_post_order)

        # Esta parte agrega soporte para CORS (Intercambio de Recursos de Origen Cruzado) para el recurso items. 
        # CORS permite que la API sea accesible desde páginas web alojadas en diferentes dominios.
        # Maneja el método HTTP OPTIONS, que es una solicitud preliminar enviada por los navegadores antes de realizar ciertos tipos de solicitudes (como POST o PUT).
        # Utiliza una Integración Simulada (Mock) para simular una respuesta con el estado 200 y establece encabezados 
        # como Access-Control-Allow-Origin, Access-Control-Allow-Methods y Access-Control-Allow-Headers 
        # para permitir solicitudes de origen cruzado.
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

# Esta parte crea un objeto App, que es la raíz de la aplicación CDK.
# Luego, instancia los stacks Ec2VpcStack y MiPrimerAPI, que definen la infraestructura EC2 y la API Gateway, respectivamente.
# Finalmente, llama a app.synth() para sintetizar (generar) la plantilla de CloudFormation, que es el resultado final que AWS utiliza para desplegar la infraestructura.
app = App()
Ec2VpcStack(app, "vpc")
MiPrimerAPI(app, "mi-api")

app.synth()

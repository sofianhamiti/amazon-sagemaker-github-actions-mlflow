import os
import yaml
import boto3
import sagemaker
from constructs import Construct
from aws_cdk import (
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    aws_sagemaker as sagemaker_,
    CfnOutput,
    Duration,
    Stack,
    App,
)


def get_model_location_from_ssm(ssm_parameter_name):
    ssm = boto3.client("ssm")
    response = ssm.get_parameter(Name=ssm_parameter_name)
    return response["Parameter"]["Value"]


class InferenceStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ==========================
        # ======== CONFIG  =========
        # ==========================
        # IAM ROLE FOR ENDPOINT AND LAMBDA FUNCTION
        iam_role = sagemaker.get_execution_role()

        # READ CONFIG
        with open("../../../cfg/model_deploy.yaml") as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

        sagemaker_model_name = f"{config['model']['name']}-{config['model']['version']}-{os.environ['DEPLOYMENT_ENV']}"

        model_s3_location = get_model_location_from_ssm(
            config["model"]["location_ssm_parameter"]
        )
        # ===========================
        # ===== SAGEMAKER MODEL =====
        # ===========================
        container = sagemaker_.CfnModel.ContainerDefinitionProperty(
            image=config["endpoint"]["image_uri"],
            model_data_url=model_s3_location,
            environment={
                "MLFLOW_DEPLOYMENT_FLAVOR_NAME": "python_function",
                "SERVING_ENVIRONMENT": "SageMaker",
            },
        )

        sagemaker_model = sagemaker_.CfnModel(
            scope=self,
            id="Model",
            execution_role_arn=iam_role,
            containers=[container],
            model_name=sagemaker_model_name,
        )

        # =====================================
        # ===== SAGEMAKER ENDPOINT CONFIG =====
        # =====================================
        product_variant = sagemaker_.CfnEndpointConfig.ProductionVariantProperty(
            model_name=sagemaker_model.attr_model_name,
            variant_name="variant-1",
            instance_type=config["endpoint"]["instance_type"],
            initial_instance_count=config["endpoint"]["instance_count"],
            initial_variant_weight=1.0,
        )

        sagemaker_endpoint_config = sagemaker_.CfnEndpointConfig(
            scope=self,
            id="EndpointConfig",
            production_variants=[product_variant],
            endpoint_config_name=sagemaker_model.attr_model_name,
        )

        # ==============================
        # ===== SAGEMAKER ENDPOINT =====
        # ==============================
        sagemaker_endpoint = sagemaker_.CfnEndpoint(
            scope=self,
            id="Endpoint",
            endpoint_config_name=sagemaker_endpoint_config.attr_endpoint_config_name,
            endpoint_name=sagemaker_model.attr_model_name,
        )

        # ==================================================
        # ================ LAMBDA FUNCTION =================
        # ==================================================
        role = iam.Role.from_role_arn(
            scope=self,
            id="role",
            role_arn=iam_role,
        )

        lambda_function = lambda_.Function(
            scope=self,
            id="lambda",
            role=role,
            function_name=sagemaker_model_name,
            code=lambda_.Code.from_asset("lambda_function"),
            handler="handler.proxy",
            runtime=lambda_.Runtime.PYTHON_3_8,
            memory_size=512,
            timeout=Duration.seconds(120),
            environment={"ENDPOINT_NAME": sagemaker_model_name},
        )

        # ==================================================
        # ================== API GATEWAY ===================
        # ==================================================
        api = apigw.LambdaRestApi(
            scope=self,
            id="api_gateway",
            rest_api_name=sagemaker_model_name,
            handler=lambda_function,
            proxy=True,
        )

        # ==================================================
        # =================== OUTPUTS ======================
        # ==================================================
        CfnOutput(
            scope=self,
            id="APIURL",
            value=api.url,
        )


app = App()
InferenceStack(app, f"InferenceStack-{os.environ['DEPLOYMENT_ENV']}")
app.synth()

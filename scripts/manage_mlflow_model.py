import os
import sys
import yaml
import logging
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.model_deploy.utils import MLflowHandler

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-model", action="store_true")
    parser.add_argument("--transition-staging", action="store_true")
    parser.add_argument("--transition-prod", action="store_true")
    args, _ = parser.parse_known_args()

    # CONFIG
    with open("cfg/model_deploy.yaml") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    # INSTANTIATE MLFLOW HANDLER
    logging.info("INSTANTIATE MLFLOW HANDLER")
    mlflow_handler = MLflowHandler(cfg=config)

    if args.prepare_model:
        # CREATE AND UPLOAD A TAR.GZ TO S3 FROM THE MLFLOW MODEL VERSION.
        logging.info("CREATE AND UPLOAD A TAR.GZ TO S3 FROM THE MLFLOW MODEL VERSION")
        mlflow_handler.prepare_sagemaker_model()

    if args.transition_staging:
        # TRANSITION MODEL TO STAGING
        mlflow_handler.transition_model_version_stage("Staging")

    if args.transition_prod:
        # TRANSITION MODEL TO PRODUCTION
        mlflow_handler.transition_model_version_stage("Production")

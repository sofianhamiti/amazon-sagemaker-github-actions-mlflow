import os
import sys
import yaml
import logging
import argparse
import sagemaker

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.model_build.pipeline import get_pipeline

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-execution", action="store_true")
    args, _ = parser.parse_known_args()

    # IAM ROLE
    iam_role = sagemaker.get_execution_role()

    # CONFIG
    with open("cfg/model_build.yaml") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    # INSTANTIATE PIPELINE
    logging.info("INSTANTIATE PIPELINE")
    pipeline = get_pipeline(iam_role=iam_role, cfg=config)

    # CREATE/UPDATE PIPELINE IN SAGEMAKER
    logging.info("CREATE/UPDATE PIPELINE IN SAGEMAKER")
    pipeline.upsert(role_arn=iam_role)

    if args.run_execution:
        # RUN PIPELINE
        logging.info("RUNNING PIPELINE")
        pipeline.start()

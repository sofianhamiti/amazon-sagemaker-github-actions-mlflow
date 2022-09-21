import os
import sys
import yaml
import logging
import sagemaker

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.model_build import jobs

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    # IAM ROLE
    iam_role = sagemaker.get_execution_role()

    # CONFIG
    with open("cfg/model_build.yaml") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    # RUN PROCESSING JOB
    logging.info("RUN PROCESSING JOB")
    processor = jobs.get_processor(iam_role=iam_role, cfg=config["processing"])
    processor.run(
        code=config["processing"]["entry_point"],
        outputs=[
            sagemaker.processing.ProcessingOutput(
                source=config["processing"]["parameters"]["output_folder"]
            ),
        ],
    )

    # GET TRAINING INPUT FROM PROCESSING OUTPUT
    processor_outputs = processor.jobs[-1].describe()["ProcessingOutputConfig"]
    training_input = processor_outputs["Outputs"][0]["S3Output"]["S3Uri"]
    logging.info(f"TRAINING INPUT: {training_input}")

    # RUN TRAINING JOB
    logging.info("RUN TRAINING JOB")
    estimator = jobs.get_estimator(iam_role=iam_role, cfg=config["training"])
    estimator.fit({"input": training_input})

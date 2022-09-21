from src.model_build.utils import ContainerEstimator
from sagemaker.processing import ScriptProcessor


def get_estimator(iam_role, cfg):
    estimator = ContainerEstimator(
        role=iam_role,
        image_uri=cfg["image_uri"],
        entry_point=cfg["entry_point"],
        source_dir=cfg["source_dir"],
        hyperparameters=cfg["hyperparameters"],
        instance_count=cfg["instance_count"],
        instance_type=cfg["instance_type"],
        disable_profiler=True,
        base_job_name=cfg["base_job_name"],
    )
    return estimator


def get_processor(iam_role, cfg):
    processor = ScriptProcessor(
        role=iam_role,
        image_uri=cfg["image_uri"],
        command=["python3"],
        env=cfg["parameters"],
        instance_count=cfg["instance_count"],
        instance_type=cfg["instance_type"],
        base_job_name=cfg["base_job_name"],
    )
    return processor

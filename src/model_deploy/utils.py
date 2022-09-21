import os
import boto3
import logging
import mlflow
import tarfile
import sagemaker
from mlflow.tracking import MlflowClient
from mlflow.tracking.artifact_utils import _download_artifact_from_uri


class MLflowHandler:
    def __init__(self, cfg):
        mlflow.set_registry_uri(cfg["model"]["tracking_uri"])
        self.client = MlflowClient()
        self.model_name = cfg["model"]["name"]
        self.model_version = cfg["model"]["version"]
        self.location_ssm_parameter = cfg["model"]["location_ssm_parameter"]
        logging.info("MLFLOW HANDLER LOADED")

    def _download_model_version_files(self):
        """
        download model version files to a local tmp folder.
        """
        model_version = self.client.get_model_version(
            name=self.model_name, version=self.model_version
        )
        artifact_uri = model_version.source
        return _download_artifact_from_uri(artifact_uri)

    @staticmethod
    def _make_tar_gz_file(output_filename, source_dir):
        """
        create a tar.gz from a directory.
        """
        with tarfile.open(output_filename, "w:gz") as tar:
            for f in os.listdir(source_dir):
                tar.add(os.path.join(source_dir, f), arcname=f)

    def _save_model_location_to_ssm(self, tar_gz_s3_location):
        ssm = boto3.client("ssm")
        ssm.put_parameter(
            Name=self.location_ssm_parameter,
            Value=tar_gz_s3_location,
            Type="String",
            Overwrite=True,
        )
        return

    def prepare_sagemaker_model(self):
        """
        create and upload a tar.gz to S3 from a chosen MLflow model version.
        """
        sagemaker_session = sagemaker.Session()
        bucket = (
            sagemaker_session.default_bucket()
        )  # you can specify other bucket name here
        prefix = f"mlflow_model/{self.model_name}-{self.model_version}"
        tmp_file = "/tmp/model.tar.gz"

        model_local_path = self._download_model_version_files()
        self._make_tar_gz_file(tmp_file, model_local_path)

        tar_gz_s3_location = sagemaker_session.upload_data(
            path=tmp_file, bucket=bucket, key_prefix=prefix
        )
        logging.info(f"model.tar.gz uploaded to {tar_gz_s3_location}")

        self._save_model_location_to_ssm(tar_gz_s3_location)
        logging.info(f"model location saved to SSM: {self.location_ssm_parameter}")

    def transition_model_version_stage(self, stage):
        """
        Transitions a model version to input stage.
        Transitions other model versions to Archived if they were in Staging or Production.
        """
        try:
            for model in self.client.search_model_versions(f"name='{self.model_name}'"):
                if model.current_stage in ["Staging", "Production"]:
                    self.client.transition_model_version_stage(
                        name=model.name, version=model.version, stage="Archived"
                    )
                    logging.info(
                        f"Transitioning {model.name}/{model.version} to Archived"
                    )

            self.client.transition_model_version_stage(
                name=self.model_name, version=self.model_version, stage=stage
            )
            logging.info(f"Model transitioned to {stage}")

        except Exception as e:
            logging.error(e)

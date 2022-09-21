import os
import json
import joblib
import logging
import argparse
import pandas as pd
from sklearn import ensemble
from sklearn.model_selection import train_test_split
import mlflow
import mlflow.sklearn

logging.basicConfig(level=logging.INFO)


def train(args):

    logging.info("READING DATA")
    df = pd.read_csv(f"{args.input_folder}/housing.csv")
    hyperparameters = json.loads(args.hyperparameters)

    logging.info("BUILDING TRAINING AND TESTING DATASET")
    X_train, X_test, y_train, y_test = train_test_split(
        df.loc[:, df.columns != hyperparameters["target"]],
        df[hyperparameters["target"]],
        test_size=0.2,
        random_state=42,
    )

    # SET REMOTE MLFLOW SERVER
    mlflow.set_tracking_uri(hyperparameters["tracking_uri"])
    mlflow.set_experiment(hyperparameters["experiment_name"])

    with mlflow.start_run():
        # LOG PARAMETERS
        params = {"n-estimators": hyperparameters["n_estimators"]}
        mlflow.log_params(params)

        # TRAIN
        logging.info("TRAINING MODEL")
        model = ensemble.RandomForestRegressor(
            n_estimators=hyperparameters["n_estimators"], random_state=42
        )
        model.fit(X_train, y_train)

        # EVALUATE ACCURACY
        logging.info("EVALUATING MODEL")
        accuracy = model.score(X_test, y_test)
        logging.info(f"Accuracy: {accuracy:.2f}")
        mlflow.log_metric(f"Accuracy", accuracy)

        # SAVE MODEL
        if hyperparameters["save_model_in_registry"]:
            # YOU CAN ADD A METRIC CONDITION HERE BEFORE REGISTERING THE MODEL
            logging.info("REGISTERING MODEL IN MLFLOW REGISTRY")
            # Make sure the IAM role has access to the MLflow artifact bucket
            mlflow.sklearn.log_model(
                sk_model=model,
                artifact_path="model",
                registered_model_name=hyperparameters["model_name"],
            )
        else:
            logging.info("LOGGING MODEL IN EXPERIMENT RUN")
            mlflow.sklearn.log_model(model, "model")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-folder", type=str, default=os.environ["SM_CHANNEL_INPUT"]
    )
    parser.add_argument("--hyperparameters", type=str, default=os.environ["SM_HPS"])
    parser.add_argument("--output-folder", type=str, default=os.environ["SM_MODEL_DIR"])
    args, _ = parser.parse_known_args()

    # train model
    model = train(args)

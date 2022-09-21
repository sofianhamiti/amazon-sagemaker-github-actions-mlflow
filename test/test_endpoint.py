import os
import yaml
import boto3
import logging
import requests

logging.basicConfig(level=logging.INFO)
api_client = boto3.client("apigateway")


def get_api_url(api_name):
    list_apis = api_client.get_rest_apis()["items"]
    api = [api for api in list_apis if api["name"] == api_name]

    api_id = api[0]["id"]
    aws_region = boto3.session.Session().region_name

    api_url = f"https://{api_id}.execute-api.{aws_region}.amazonaws.com/prod"
    return api_url


def test_api(url, payload):
    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()  # if status !=200 raise exception
        logging.info("SUCCESS: THE API WORKS!")

    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


if __name__ == "__main__":
    # CONFIG
    with open("cfg/model_deploy.yaml") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    # GET ENDPOINT NAME FROM CONFIG AND DEPLOYMENT ENVIRONMENT
    logging.info("GET API NAME FROM CONFIG AND DEPLOYMENT ENVIRONMENT")
    api_name = f"{config['model']['name']}-{config['model']['version']}-{os.environ['DEPLOYMENT_ENV']}"
    # GET API URL FROM NAME
    api_url = get_api_url(api_name)

    # SEND A TEST DATA POINT TO THE API AND VERIFYING THE RESPONSE STATUS CODE
    test_payload = {
        "columns": [
            "MedInc",
            "HouseAge",
            "AveRooms",
            "AveBedrms",
            "Population",
            "AveOccup",
            "Latitude",
            "Longitude",
        ],
        "index": [0],
        "data": [
            [8.3252, 41, 6.9841269841, 1.0238095238, 322, 2.5555555556, 37.88, -122.23]
        ],
    }

    results = test_api(api_url, test_payload)

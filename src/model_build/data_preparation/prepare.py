import os
import logging
import pandas as pd
from sklearn import datasets

logging.basicConfig(level=logging.INFO)


def prepare_data():
    # GET DATASET FROM SCIKIT-LEARN
    logging.info("GET DATASET FROM SCIKIT-LEARN")
    df = datasets.fetch_california_housing(as_frame=True).frame

    # SAVE DATASET INTO CSV FILE
    logging.info("SAVE DATASET INTO CSV FILE")
    df.to_csv(f"{os.environ['output_folder']}/housing.csv", sep=",", index=False)


if __name__ == "__main__":
    prepare_data()

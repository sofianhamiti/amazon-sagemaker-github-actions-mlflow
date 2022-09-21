import joblib
import pandas as pd
from sklearn import datasets
from sklearn import ensemble
from sklearn.model_selection import train_test_split


def prepare_data():
    df = datasets.fetch_california_housing(as_frame=True).frame

    housing_df = pd.read_csv("sandbox/data/housing.csv")

    X_train, X_test, y_train, y_test = train_test_split(
        housing_df.loc[:, housing_df.columns != "MedHouseVal"],
        housing_df["MedHouseVal"],
        test_size=0.2,
        random_state=42,
    )
    return X_train, X_test, y_train, y_test


def train(X_train, y_train):
    model = ensemble.RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    return model


def evaluate(X_test, y_test):
    accuracy = model.score(X_test, y_test)
    print(f"Accuracy: {accuracy:.2f}")


if __name__ == "__main__":
    X_train, X_test, y_train, y_test = prepare_data()

    # train model
    model = train(X_train, y_train)

    # evaluate
    evaluate(X_test, y_test)

    # save model
    joblib.dump(model, "sandbox/model/rf_model.joblib")

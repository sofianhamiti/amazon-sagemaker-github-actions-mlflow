FROM python:3.8-slim

ENV PYTHONUNBUFFERED=TRUE

# install gcc
RUN apt-get update \
    && apt-get install -y gcc git \
    && apt-get clean

# install python dependencies
RUN pip install --no-cache --upgrade \
    scikit-learn==1.1.2 \
    mlflow==1.28.0 \
    sagemaker-training==4.2.6
#!/usr/bin/env bash

source /home/ec2-user/.profile
act -j deploy-prod -s IAM_ROLE=<your IAM role ARN> -s AWS_REGION=<your region name> -s ACCOUNT_ID=12345567778 -P ubuntu-latest=catthehacker/ubuntu:act-latest

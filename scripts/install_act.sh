#!/usr/bin/env bash

curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
echo 'export PATH=/home/ec2-user/bin/:$PATH' >> /home/ec2-user/.profile

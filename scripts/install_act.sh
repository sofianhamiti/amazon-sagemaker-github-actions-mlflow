#!/usr/bin/env bash

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

echo 'eval "$(/home/ec2-user/.linuxbrew/bin/brew shellenv)"' >> /home/ec2-user/.profile
eval "$(/home/ec2-user/.linuxbrew/bin/brew shellenv)"

sudo yum groupinstall -y 'Development Tools'

brew install gcc act

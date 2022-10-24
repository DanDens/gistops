#!/bin/bash
set -e

############
# Packages #
############
sudo apt-get update && sudo apt upgrade 
sudo apt-get install software-properties-common --allow-unauthenticated -y --fix-missing
sudo apt-get install --allow-unauthenticated -y --fix-missing \
  apt-utils \
  unzip \
  curl \
  gnupg \
  lsb-release \
  apt-transport-https \
  ca-certificates \
  dirmngr \
  wget \
  gpg \
  jq 

##########
# Docker #
##########
# Cloud9 ships with docker already

###############
# Python 3.10 #
###############
sudo apt install -y build-essential libncursesw5-dev libssl-dev \
  libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev  

python_version="$(python3.10 --version 2>/dev/null)" || true
if ! [ "$python_version" = "Python 3.10.8" ];
then  
  # From https://www.python.org/downloads/release/python-3108/
  curl https://www.python.org/ftp/python/3.10.8/Python-3.10.8.tgz -o Python-3.10.8.tgz 
  if [ -z "$(md5sum Python-3.10.8.tgz | grep fbe3fff11893916ad1756b15c8a48834)" ];
  then
    echo "md5 checksum of https://www.python.org/ftp/python/3.10.8/Python-3.10.8.tgz is not fbe3fff11893916ad1756b15c8a48834."
    echo "Please double check on https://www.python.org/downloads/release/python-3108/"
    exit 100
  fi

  tar xzf Python-3.10.8.tgz 

  # install
  pushd .
  cd Python-3.10.8 
  ./configure --enable-optimizations
  sudo make altinstall 
  popd

  sudo update-alternatives --install /usr/bin/python python /usr/local/bin/python3.10 2
  sudo update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.10 2

  # cleanup
  sudo rm -rf Python-3.10.8
  sudo rm Python-3.10.8.tgz
fi

pip_available="$(python3.10 -m pip --version | grep 'python3.10')" || true
if [ -z "$pip_available" ];
then 
  # Install latest pip
  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
  sudo python3.10 get-pip.py 
  rm get-pip.py
fi 

# Install python packages
python3.10 -m pip install -r ../../gistops/requirements.txt

###########
# AWS CLI #
###########
aws_version="$(aws --version | grep 'aws-cli/')" || true
if [ -z "$aws_version" ];
then  
  # We need to fix AWS CLI after the update
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
  unzip awscliv2.zip
  sudo ./aws/install
  
  rm -rf ./aws
  rm awscliv2.zip
fi




exit 0 
#!/bin/bash
set -e

############
# Packages #
############
sudo yum update && sudo yum upgrade 
sudo yum install -y  \
  unzip \
  curl \
  gnupg2 \
  ca-certificates \
  wget \
  jq \
  pandoc \
  texlive \
  librsvg2 \
  git \
  gnupg

##########
# Docker #
##########
# Cloud9 ships with docker already

###############
# Python 3.10 #
###############
sudo yum -y groupinstall "Development Tools"
sudo yum remove -y openssl openssl-devel
sudo yum install -y gcc devel libffi-devel openssl11 openssl11-devel bzip2-devel

python310_version="$(python3.10 --version 2>/dev/null)" || true
if ! [ "$python310_version" = "Python 3.10.8" ];
then  
  # From https://www.python.org/downloads/release/python-3108/
  curl -sS https://www.python.org/ftp/python/3.10.8/Python-3.10.8.tgz -o Python-3.10.8.tgz 
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

  sudo update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.10 2
  sudo update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.7 3
  
  # cleanup
  sudo rm -rf ./Python-3.10.8
  sudo rm Python-3.10.8.tgz
fi

pip310_available="$(python3.10 -m pip --version | grep 'python3.10')" || true
if [ -z "$pip310_available" ];
then 
  # Install latest pip
  curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
  sudo python3.10 get-pip.py 
  rm get-pip.py
fi 

##############
# Python 3.7 #
##############
python37_version="$(python3.7 --version)" || true
if ! [ "$python37_version" = "Python 3.7.15" ];
then  
  # From https://www.python.org/downloads/release/python-3715/
  curl -sS https://www.python.org/ftp/python/3.7.15/Python-3.7.15.tgz -o Python-3.7.15.tgz 
  if [ -z "$(md5sum Python-3.7.15.tgz | grep beff0cd66129ad1761632aafd72ac866)" ];
  then
    echo "md5 checksum of https://www.python.org/ftp/python/3.7.15/Python-3.7.15.tgz is not beff0cd66129ad1761632aafd72ac866."
    echo "Please double check on https://www.python.org/downloads/release/python-3715/"
    exit 100
  fi

  tar xzf Python-3.7.15.tgz

  # install
  pushd .
  cd Python-3.7.15 
  ./configure --enable-optimizations
  sudo make altinstall 
  popd

  sudo update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.7 3

  # cleanup
  sudo rm -rf Python-3.7.15
  sudo rm Python-3.7.15.tgz
fi

pip37_available="$(python3.7 -m pip --version | grep 'python3.7')" || true
if [ -z "$pip37_available" ];
then 
  # Install latest pip
  curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
  sudo python3.7 get-pip.py 
  rm get-pip.py
fi 

###########
# AWS CLI #
###########
aws_version="$(aws --version | grep 'aws-cli/')" || true
if [ -z "$aws_version" ];
then  
  # We need to fix AWS CLI after the update
  curl -sS "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
  unzip awscliv2.zip
  sudo ./aws/install
  
  rm -rf ./aws
  rm awscliv2.zip
fi

#####################
# GIT Configuration #
#####################
git config --global credential.helper store
git config --global http.sslverify true

#############
# GIT Alias #
#############
git config --global core.editor "nano"
git config --global alias.lol "log --oneline --graph --decorate --all"
git config --global alias.wcd "whatchanged -p --abbrev-commit --pretty=medium"
git config --global alias.mtn "mergetool --no-prompt"
git config --global alias.sts "status -s" 
git config --global alias.acp '!acp() { git add . && git commit -m "$1" && git push ${2-origin} ; }; acp'

git config --global --list


exit 0 
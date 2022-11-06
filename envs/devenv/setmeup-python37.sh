#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive

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

exit 0 
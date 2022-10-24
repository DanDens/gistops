#!/usr/bin/env sh
set -e

################
# APT PACKAGES #
################
sudo apt-get update && sudo apt upgrade 
sudo apt-get install software-properties-common --allow-unauthenticated -y --fix-missing
sudo apt-get install --allow-unauthenticated -y --fix-missing \
  apt-utils \
  unzip \
  curl \
  apt-transport-https \
  ca-certificates \
  dirmngr \
  wget \
  gpg \
  jq 

###############
# Python 3.10 #
###############
sudo apt install -y build-essential libncursesw5-dev libssl-dev \
  libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev  

python_version="$(python3.10 --version)" || true
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

  sudo update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.10 2

  # cleanup
  rm -rf Python-3.10.8
  rm Python-3.10.8.tgz
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

#####################
# GIT Configuration #
#####################
git config credential.helper store
git config http.sslverify true

#############
# GIT Alias #
#############
git config alias.lol "log --oneline --graph --decorate --all"
git config alias.wcd "whatchanged -p --abbrev-commit --pretty=medium"
git config alias.mtn "mergetool --no-prompt"
git config alias.sts "status -s" 
git config alias.acp '!acp() { git add . && git commit -m "$1" && git push ${2-origin} ; }; acp'

exit 0 
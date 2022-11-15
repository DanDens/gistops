#!/bin/bash
set -e

python3 -m pip install --upgrade pip
python3 -m pip install virtualenv
python3 -m venv ./venv

source ./venv/bin/activate

python3 -m pip install -r requirements.txt
python3 -m pip install pylint
python3 -m pip install pytest
python3 -m pip install pytest-mock
python3 -m pip install beautifulsoup4

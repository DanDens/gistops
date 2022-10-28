#!/bin/bash
set -e

python3.10 -m pip install --user --upgrade pip
python3.10 -m pip install --user virtualenv
python3.10 -m venv ./venv

source ./venv/bin/activate

python3.10 -m pip install -r ./requirements.txt
python3.10 -m pip install pylint

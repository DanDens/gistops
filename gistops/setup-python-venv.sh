#!/bin/bash
set -e

python3.7 -m pip install --user --upgrade pip
python3.7 -m pip install --user virtualenv
python3.7 -m venv ./venv

source ./venv/bin/activate

python3.7 -m pip install -r ./requirements.txt
# For interactive debugging in cloud9
python3.7 -m pip install ikp3db

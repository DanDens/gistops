#!/bin/bash
set -e

python3.10 -m pip install --user --upgrade pip
python3.10 -m pip install --user virtualenv
python3.10 -m venv ./gistops/venv

source ./gistops/venv/bin/activate

python3.10 -m pip install -r ./gistops/requirements.txt

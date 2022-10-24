#!/usr/bin/env python3
import os
import sys
from pathlib import Path
# adjust PYTHON_PATH for debugging of lambda app
sys.path.append(str(Path(os.path.realpath(__file__)).parent))
import logging
import json
from typing import List

import fire


def run():
  logger = logging.getLogger()
  logger.addHandler(logging.StreamHandler(sys.stdout))
  logger.setLevel(logging.INFO)
  
  logger.info('hi')

  # todo: 
  # https://www.freecodecamp.org/news/how-to-use-github-as-a-pypi-server-1c3b0d07db2/
  # https://gnupg.readthedocs.io/en/latest/

def main():
  fire.Fire(run)
  
  
if __name__ == '__main__':
  main()

#!/usr/bin/env python3
# Copyright Notice
# Author jens.orthmann@gmail.com

# Permission is hereby granted, free of charge, to any person obtaining a copy of 
# this software and associated documentation files (the "Software"), to deal in the 
# Software without restriction, including without limitation the rights to use, copy, 
# modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
# and to permit persons to whom the Software is furnished to do so, subject to the 
# following conditions:

# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR 
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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

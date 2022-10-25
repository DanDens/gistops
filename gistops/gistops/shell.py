#!/usr/bin/env python3
import os
from typing import List
from pathlib import Path
import logging

from invoke import run as __run


def run(cmd: List[str], env: dict = os.environ, silent: bool = False):
  if not silent:
    logger = logging.getLogger()
    logger.info(" ".join(cmd))

  return __run(shell='sh', command=" ".join(cmd), hide=silent, env=env).stdout

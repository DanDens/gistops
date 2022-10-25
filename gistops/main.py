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


class GistOpsRemote(object):
  """Copy&paste operations with remote gist repositories"""

  def push(self, 
    branch_regex: str, 
    git_remote_url: str=os.environ['GISTOPS_GIT_REMOTE_URL'], 
    git_root: Path=Path.cwd(),
    silent: bool=False):
    """Push mirror branch(es) to remote"""
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)

    from gistops.remote import push
    push(branch_regex,git_remote_url,git_root,silent)


  def pull(self, 
    branch_regex: str, 
    git_remote_url:str=os.environ['GISTOPS_GIT_REMOTE_URL'], 
    git_root: Path=Path.cwd(),
    silent: bool=False):
    """Pull mirror branch(es) from remote"""
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)
    
    from gistops.remote import pull
    pull(branch_regex,git_remote_url,git_root,silent)


class GistOps(object):
  """Operations for gists (in git repositories)"""

  def __init__(self):
    self.remote = GistOpsRemote()
  

def main():
  fire.Fire(GistOps)


if __name__ == '__main__':
  main()

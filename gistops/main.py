#!/usr/bin/env python3
import os
import sys
import logging
from functools import partial
from pathlib import Path

import fire

# adjust PYTHON_PATH for debugging of lambda app
sys.path.append(str(Path(os.path.realpath(__file__)).parent))
from gistops.gistops.mirror import mirror as gistops_mirror
from gistops.gistops.mirror import compile_remote as gistops_compile_remote
from gistops.gistops.mirror import GitRemote
from gistops.shell import shell as gistops_shell

# adjust PYTHON_PATH for debugging of lambda app
sys.path.append(str(Path(os.path.realpath(__file__)).parent))

class GistOpsRemote(object):
    """Copy&paste operations with remote gist repositories"""

    def __init__(self,
        git_path: str=str(Path.cwd()),
        silent_cmd:bool=False,
        silent_run:bool=False):

        self.__shell = partial(
          gistops_shell,
          env=os.environ,
          cwd=Path(git_path).resolve(),
          silent_cmd=silent_cmd,
          silent_run=silent_run)


    def mirror( self,
      branch_regex: str,
      git_source_url: str=os.environ['GISTOPS_GIT_SOURCE_URL'],
      git_source_username: str=os.environ['GISTOPS_GIT_SOURCE_USERNAME'],
      git_source_password: str=os.environ['GISTOPS_GIT_SOURCE_PASSWORD'],
      git_target_url: str=os.environ['GISTOPS_GIT_TARGET_URL'],
      git_target_username: str=os.environ['GISTOPS_GIT_TARGET_USERNAME'],
      git_target_password: str=os.environ['GISTOPS_GIT_TARGET_PASSWORD']):
        """Push mirror branch(es) to remote"""
        logger = logging.getLogger()
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(logging.INFO)

        gistops_mirror(
            shell=self.__shell,
            git_remote_source = gistops_compile_remote(
              git_source_url, git_source_username, git_source_password
            ),
            git_remote_target = gistops_compile_remote(
              git_target_url, git_target_username, git_target_password
            ),
            branch_regex=branch_regex)


class GistOps(object):
    """Operations for gists (in git repositories)"""

    def __init__(self):
        self.remote = GistOpsRemote()


if __name__ == '__main__':
    fire.Fire(GistOps)

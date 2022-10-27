#!/usr/bin/env python3
import os
import sys
import logging
from functools import partial
from pathlib import Path
from typing import Callable, List

import fire

# adjust PYTHON_PATH for debugging of lambda app
sys.path.append(str(Path(os.path.realpath(__file__)).parent))
from gistops.gists import Gist, locate_git_root, iterate_gists
from gistops.shell import shrun
from gistops.mirror import mirror, as_remote, GitRemote
from gistops.render import render
from gistops.publish import publish


class GistOps(object):
    """Operations for gists (in git repositories)"""


    def __init__(self, 
      gist_path: str=str(Path.cwd()), 
      git_diff_hash: str=None,
      quiet: bool=False):
        # Configure logging
        logger = logging.getLogger()
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(os.environ.get('LOG_LEVEL','INFO'))
           
        # Remember parameters
        self.__git_diff_hash = git_diff_hash
        # Make git root current working directory 
        # and make path relative to git root
        self.__git_root = locate_git_root(Path(gist_path).resolve())
        os.chdir(str(self.__git_root))
        self.__gist_path = Path(gist_path).relative_to(self.__git_root)
        
        # Pre-configure shell runner
        self.__shrun: Callable[[List[str]], str] = partial(
          shrun,
          env=os.environ,
          cwd=self.__git_root.resolve(),
          hide_streams=False,
          log_cmd_level=logging.INFO,
          enforce_absolute_silence=quiet) 
          

    def render(self):
        """Render gists as defined by .gitattributes"""
        for gist in iterate_gists(
          shrun=self.__shrun, 
          git_root=self.__git_root, 
          gist_path=self.__gist_path, 
          git_diff_hash=self.__git_diff_hash):
            render(shrun=self.__shrun, gist=gist)
    
    
    def publish(self):
        """Publish gists as defined by .gitattributes"""
        for gist in iterate_gists(
          shrun=self.__shrun, 
          git_root=self.__git_root, 
          gist_path=self.__gist_path, 
          git_diff_hash=self.__git_diff_hash):
            publish(shrun=self.__shrun, gist=gist)


    def mirror(self,
      branch_regex: str,
      git_src_url: str=os.environ['GISTOPS_GIT_SOURCE_URL'],
      git_trg_url: str=os.environ['GISTOPS_GIT_TARGET_URL'],
      git_src_username: str=os.environ.get('GISTOPS_GIT_SOURCE_USERNAME', None),
      git_src_password: str=os.environ.get('GISTOPS_GIT_SOURCE_PASSWORD', None),
      git_trg_username: str=os.environ.get('GISTOPS_GIT_TARGET_USERNAME', None),
      git_trg_password: str=os.environ.get('GISTOPS_GIT_TARGET_PASSWORD', None) ):
        """Push mirror branch(es) to remote"""
        
        mirror(
          shrun = self.__shrun,
          git_remote_src = as_remote(
            self.__shrun, git_src_url, git_src_username, git_src_password ),
          git_remote_trg = as_remote(
            self.__shrun, git_trg_url, git_trg_username, git_trg_password ),
          branch_regex = branch_regex)


if __name__ == '__main__':
    fire.Fire(GistOps)

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
from gistops.git_mirror import mirror_remote, to_remote, GitRemote
from gistops.pandoc_convert import convert_gist


class GistOps(object):
    """Operations for gists (in git repositories)"""


    def __init__(self, gist_path: str=str(Path.cwd()), silent: bool=False):
        logger = logging.getLogger()
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(logging.INFO)
           
        self.__git_root = locate_git_root(
            gist_absolute_path=Path(gist_path).resolve())
        os.chdir(str(self.__git_root))
        self.__gist_path = Path(gist_path).relative_to(self.__git_root)
        
        self.__shrun: Callable[[List[str],bool], str] = partial(
          shrun,
          env=os.environ,
          cwd=self.__git_root.resolve(),
          silent_streams=silent) 
          

    def convert(self):
        """Render gists using config stored as .gitattributes"""
        
        for gist in iterate_gists(
          self.__shrun, self.__git_root, self.__gist_path):
            convert_gist(shrun=self.__shrun, gist=gist)
            
            
    # def publish(self):
    #     """Publish gists using information stored as .gitattributes"""
        
                

    def mirror(self,
      branch_regex: str,
      git_source_url: str=os.environ['GISTOPS_GIT_SOURCE_URL'],
      git_source_username: str=os.environ['GISTOPS_GIT_SOURCE_USERNAME'],
      git_source_password: str=os.environ['GISTOPS_GIT_SOURCE_PASSWORD'],
      git_target_url: str=os.environ['GISTOPS_GIT_TARGET_URL'],
      git_target_username: str=os.environ['GISTOPS_GIT_TARGET_USERNAME'],
      git_target_password: str=os.environ['GISTOPS_GIT_TARGET_PASSWORD']):
        """Push mirror branch(es) to remote"""
        
        mirror_remote(
            shrun=self.__shrun,
            git_remote_source=to_remote(
              git_source_url, git_source_username, git_source_password ),
            git_remote_target=to_remote(
              git_target_url, git_target_username, git_target_password ),
            branch_regex=branch_regex)


if __name__ == '__main__':
    fire.Fire(GistOps)

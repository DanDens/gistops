#!/usr/bin/env python3
"""
Command line arguments for GistOps Operations
"""
import os
import json
import logging
from functools import partial
from pathlib import Path
from typing import Callable, List

import fire

import gists
import shell
import version


class GistOps():
    """gistops - Operations on Gists managed by Git"""


    def __init__(self, 
      cwd: str = str( Path.cwd() ), 
      git_hash: str = None,
      protected_envs: List[str] = os.environ.get('GISTOPS_PROTECTED_ENVS', [])):

        logger = logging.getLogger()
        logfile = logging.FileHandler(Path(cwd).joinpath('gistops.log'))
        logfile.setFormatter(logging.Formatter(
            '%(levelname)s %(asctime)s %(message)s'))
        logger.addHandler(logfile)
        logger.setLevel(os.environ.get('LOG_LEVEL','INFO'))

        logger.info(version.__version__)

        ############
        # Git Root #
        ############
        # Remember parameters
        self.__git_diff_hash = git_hash
        # Make git root current working directory 
        # and make path relative to git root
        self.__git_root = gists.assert_git_root(Path(cwd).resolve())
        # Important as gist.path is a unique key
        os.chdir(str(self.__git_root)) 
        self.__gist_path = Path(cwd).relative_to(self.__git_root)

        ##################
        # Protected Envs #
        ##################
        # Remove sensitive keys from os.environ 
        # when running executables on the shell
        protected_envs.extend([
          'GISTOPS_GIT_SOURCE_URL',
          'GISTOPS_GIT_SOURCE_USERNAME',
          'GISTOPS_GIT_SOURCE_PASSWORD',
          'GISTOPS_GIT_TARGET_URL',
          'GISTOPS_GIT_TARGET_USERNAME',
          'GISTOPS_GIT_TARGET_PASSWORD'
        ])
        shell_env = os.environ.copy()
        for protected_key in protected_envs:
            if protected_key in shell_env: 
                del shell_env[protected_key]

        #######################
        # Pre-configure Shell #
        #######################
        self.__shrun: Callable[[List[str]], str] = partial(
          shell.shrun,
          env=shell_env,
          cwd=self.__git_root.resolve()) 

        ##########################
        # Pre-configure Iterator #
        ##########################
        self.__iterate_gists = partial(
          gists.iterate_gists, 
          git_root=self.__git_root, 
          gist_path=self.__gist_path, 
          git_diff_hash=self.__git_diff_hash)


    def init(self):
        """Initializes gistops for the git repository"""
        
        gists.init_gistops(self.__shrun,self.__git_root)
        
    
    def version(self) -> str:
        """Just print the version"""
        logger = logging.getLogger()
        logger.info(version.__version__)


    def iterate(self):
        """Convert gists using *.pandoc.yml"""

        event = json.dumps(
          {'gists':[gists.gist_to_basic_dict(g) for g in self.__iterate_gists(self.__shrun)]} )

        print( event )
        

def main():
    """gistops cli entrypoint"""
    fire.Fire(GistOps)


if __name__ == '__main__':
    main()

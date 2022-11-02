#!/usr/bin/env python3
"""
Command line arguments for GistOps Operations
"""
import os
import logging
from functools import partial
from pathlib import Path
from typing import Callable, List

import fire

import gists
import iterate
import shell
import version


class GistOps():
    """gistops - Operations on Gists managed by Git"""


    def __init__(self, 
      cwd: str = str( Path.cwd() ), 
      git_hash: str = None):

        logger = logging.getLogger()
        logfile = logging.FileHandler(
          Path(cwd).joinpath('gistops.log'))
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
        self.__git_root = gists.assert_git_root(
          Path(cwd).resolve())
        # Important as gist.path is a unique key
        os.chdir(str(self.__git_root)) 
        self.__gist_path = Path(
          cwd).relative_to(self.__git_root)

        #######################
        # Pre-configure Shell #
        #######################
        self.__shrun: Callable[[List[str]], str] = partial(
          shell.shrun,
          env=os.environ,
          cwd=self.__git_root.resolve()) 

        ##########################
        # Pre-configure Iterator #
        ##########################
        self.__iterate_gists = partial(
          iterate.iterate_gists, 
          git_root=self.__git_root, 
          gist_path=self.__gist_path, 
          git_diff_hash=self.__git_diff_hash)


    def init(self):
        """Initializes gistops for the git repository"""
        
        gists.init_gistops(self.__shrun,self.__git_root)


    def version(self) -> str:
        """Just print the version"""
        return version.__version__


    def iterate(self) -> str:
        """Iterate gists in git tree (that have changed)"""
        return gists.to_event( 
          list(self.__iterate_gists(self.__shrun)) )


def main():
    """gistops entrypoint"""
    fire.Fire(GistOps)


if __name__ == '__main__':
    main()

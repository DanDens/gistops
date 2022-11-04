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
import shell
import mirroring
import version


class GistOps():
    """gistops - Operations on Gists managed by Git"""


    def __init__(self, 
      cwd: str = str(Path.cwd()), 
      dry_run: bool = False ):

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
        # Make git root current working directory 
        # and make path relative to git root
        self.__git_root = gists.assert_git_root(Path(cwd).resolve())
        # Important as gist.path is a unique key
        os.chdir(str(self.__git_root)) 

        #######################
        # Pre-configure Shell #
        #######################
        self.__shrun: Callable[[List[str]], str] = partial(
          shell.shrun,
          env=os.environ,
          cwd=self.__git_root.resolve()) 

        self.__dry_run = dry_run


    def version(self) -> str:
        """Just print the version"""
        return version.__version__


    def mirror(self,
      branch_regex: str,
      git_src_url: str = None,
      git_trg_url: str = None,
      git_src_username: str = None,
      git_src_password: str = None,
      git_trg_username: str = None,
      git_trg_password: str = None ):
        """Push mirror branch(s) to remote"""
        logger = logging.getLogger()

        if git_src_url is None: 
            git_src_url=os.environ.get('GISTOPS_GIT_SOURCE_URL', None)
        if git_trg_url is None: 
            git_trg_url=os.environ.get('GISTOPS_GIT_TARGET_URL', None)

        if git_src_url is None or git_trg_url is None:
            logger.info('Either src or target is not set, skipping ...')
            return

        if git_src_username is None:
            git_src_username=os.environ.get('GISTOPS_GIT_SOURCE_USERNAME', None)
        if git_src_password is None:
            git_src_password=os.environ.get('GISTOPS_GIT_SOURCE_PASSWORD', None)
        if git_trg_username is None:
            git_trg_username=os.environ.get('GISTOPS_GIT_TARGET_USERNAME', None)
        if git_trg_password is None:
            git_trg_password=os.environ.get('GISTOPS_GIT_TARGET_PASSWORD', None)

        mirroring.mirror(
          shrun = self.__shrun,
          git_remote_src = mirroring.as_remote(
            self.__shrun, git_src_url, git_src_username, git_src_password ),
          git_remote_trg = mirroring.as_remote(
            self.__shrun, git_trg_url, git_trg_username, git_trg_password ),
          branch_regex = branch_regex,
          dry_run = self.__dry_run)


    def run(self,
      branch_regex: str,
      git_src_url: str = None,
      git_trg_url: str = None,
      git_src_username: str = None,
      git_src_password: str = None,
      git_trg_username: str = None,
      git_trg_password: str = None ) -> str:
        """Iterate gists in git tree (that have changed)"""
        return self.mirror(
          branch_regex,
          git_src_url,
          git_trg_url,
          git_src_username,
          git_src_password,
          git_trg_username,
          git_trg_password)


def main():
    """gistops entrypoint"""
    fire.Fire(GistOps)


if __name__ == '__main__':
    main()

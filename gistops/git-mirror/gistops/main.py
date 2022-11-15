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
      logsdir: str = None,
      dry_run: bool = False ):

        logspath = Path(logsdir) if logsdir is not None else Path(cwd)
        logspath.mkdir(parents=True, exist_ok=True)
        datefmt='%Y-%m-%dT%H:%M:%SZ'

        # Logs to gistops.log
        logger = logging.getLogger()
        logfile = logging.FileHandler(
          logspath.joinpath('gistops.log'))
        logfile.setFormatter(logging.Formatter(
            'git-mirror,%(levelname)s,%(asctime)s,%(message)s', datefmt=datefmt ))
        logger.addHandler(logfile)
        logger.setLevel(os.environ.get('LOG_LEVEL','INFO'))
        logger.info(version.__version__)

        # Trailing to gistops.trail
        traillog = logging.getLogger('gistops.trail')
        traillogfile = logging.FileHandler(
          logspath.joinpath('gistops.trail'))
        traillogfile.setFormatter(logging.Formatter(
            'git-mirror,%(levelname)s,%(asctime)s,%(message)s', datefmt=datefmt ))
        traillog.addHandler(traillogfile)
        traillog.setLevel(os.environ.get('LOG_LEVEL','INFO'))

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
      git_trg_password: str = None,
      delete_src: bool = False ):
        """Copy branch(es) from src to trg remote"""
        try:
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
              delete_src = delete_src,
              dry_run = self.__dry_run)

            logging.getLogger('gistops.trail').info(f'*,mirrored to {git_trg_url}')

        except Exception as err:
            logging.getLogger('gistops.trail').error(f'*,mirroring to {git_trg_url} failed')
            logging.getLogger().error(str(err))
            raise err

    def run(self,
      branch_regex: str,
      git_src_url: str = None,
      git_trg_url: str = None,
      git_src_username: str = None,
      git_src_password: str = None,
      git_trg_username: str = None,
      git_trg_password: str = None,
      delete_src: bool = False ) -> str:
        """Copy branch(es) from src to trg remote"""
        return self.mirror(
          branch_regex,
          git_src_url,
          git_trg_url,
          git_src_username,
          git_src_password,
          git_trg_username,
          git_trg_password,
          delete_src = delete_src)


def main():
    """gistops entrypoint"""
    fire.Fire(GistOps)


if __name__ == '__main__':
    main()

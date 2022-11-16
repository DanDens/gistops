#!/usr/bin/env python3
"""
Command line arguments for GistOps Operations
"""
import os
import logging
import json
from functools import partial
from pathlib import Path
from typing import Callable, List

import fire

import gists
import iterate
import shell
import version


class GistOps():
    """gistops - iterate gists stored in git"""

    def __logs(self, logspath: Path, prefix: str='git-ls-attr'):
        logspath.mkdir(parents=True, exist_ok=True)
        datefmt='%Y-%m-%dT%H:%M:%SZ'

        # Logs to gistops.log
        logger = logging.getLogger()
        logfile = logging.FileHandler(
          logspath.joinpath(f'{prefix}.gistops.log'))
        logfile.setFormatter(logging.Formatter(
            f'{prefix},%(levelname)s,%(asctime)s,%(message)s', datefmt=datefmt ))
        logger.addHandler(logfile)
        logger.setLevel(os.environ.get('LOG_LEVEL','INFO'))
        logger.info(version.__version__)

        # Trailing to gistops.trail
        traillog = logging.getLogger('gistops.trail')
        traillogfile = logging.FileHandler(
          logspath.joinpath(f'{prefix}.gistops.trail'))
        traillogfile.setFormatter(logging.Formatter(
            f'{prefix},%(levelname)s,%(asctime)s,%(message)s', datefmt=datefmt ))
        traillog.addHandler(traillogfile)
        traillog.setLevel(os.environ.get('LOG_LEVEL','INFO'))


    def __init__(self, 
      cwd: str = str( Path.cwd() ),
      logsdir: str=None ):

        self.__logs( logspath=Path(logsdir) if logsdir is not None else Path(cwd) )

        ############
        # Git Root #
        ############
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


    def version(self) -> str:
        """print the version"""
        return version.__version__


    def list(self, git_hash: str = None) -> str:
        """iterate gists in git"""

        try:
            with open(Path.cwd().joinpath('gists.json'), 'w', encoding='utf-8') as gists_file:
                gists_file.write(
                  json.dumps( [gists.to_basic_dict(gist) for gist in iterate.iterate_gists(
                    shrun=self.__shrun,
                    git_root=self.__git_root, 
                    gist_path=self.__gist_path, 
                    git_diff_hash=None)] ) )

            gsts: List[gists.Gist] = list()
            for gist in iterate.iterate_gists(
              shrun=self.__shrun,
              git_root=self.__git_root, 
              gist_path=self.__gist_path, 
              git_diff_hash=git_hash):

                gsts.append(gist)
                logging.getLogger('gistops.trail').info(f'{gist.path},triggered')

            return gists.to_event(gsts)

        except Exception as err:
            logging.getLogger('gistops.trail').error('*,unexpected error')
            logging.getLogger().error(str(err))
            raise err


    def run(self, git_hash: str = None) -> str:
        """iterate gists in git"""
        return self.list(git_hash=git_hash)


def main():
    """gistops entrypoint"""
    fire.Fire(GistOps)


if __name__ == '__main__':
    main()

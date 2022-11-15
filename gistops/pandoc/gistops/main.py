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
import converting
import version


class GistOps():
    """gistops - Operations on Gists managed by Git"""


    def __init__(self, 
      cwd: str = str(Path.cwd()), 
      logsdir: str = None,
      dry_run: bool = False):

        logspath = Path(logsdir) if logsdir is not None else Path(cwd)
        logspath.mkdir(parents=True, exist_ok=True)
        datefmt='%Y-%m-%dT%H:%M:%SZ'

        # Logs to gistops.log
        logger = logging.getLogger()
        logfile = logging.FileHandler(
          logspath.joinpath('gistops.log'))
        logfile.setFormatter(logging.Formatter(
            'pandoc,%(levelname)s,%(asctime)s,%(message)s', datefmt=datefmt ))
        logger.addHandler(logfile)
        logger.setLevel(os.environ.get('LOG_LEVEL','INFO'))
        logger.info(version.__version__)

        # Trailing to gistops.trail
        traillog = logging.getLogger('gistops.trail')
        traillogfile = logging.FileHandler(
          logspath.joinpath('gistops.trail'))
        traillogfile.setFormatter(logging.Formatter(
            'pandoc,%(levelname)s,%(asctime)s,%(message)s', datefmt=datefmt ))
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


    def convert(self, event_base64: str, outpath: str='.') -> str:
        """Convert gists using *.pandoc.yml"""
        try:
            try:
                outpath = Path(outpath).resolve().relative_to(self.__git_root.resolve())
            except ValueError as err:
                raise gists.GistOpsError(
                  'output path MUST be sub directory of git root'
                  'in order to be accessable from downstream ops') from err

            convs: List[gists.ConvertedGist] = []
            for gist in gists.from_event(event_base64):
                try:
                    convs.extend(
                      converting.convert(
                        shrun=self.__shrun, 
                        gist=gist, 
                        outpath=Path(outpath),
                        dry_run=self.__dry_run) )

                    logging.getLogger('gistops.trail').info(f'{gist.path},convertion failed')

                except Exception as err:
                    logging.getLogger('gistops.trail').error(f'{gist.path},convertion failed')
                    raise err
                
            return gists.to_event( convs )
      
        except Exception as err:
            logging.getLogger('gistops.trail').error('*,unexpected error')
            logging.getLogger().error(str(err))
            raise err


    def run(self, event_base64: str, outpath: str='.') -> str:
        """Convert gists using *.pandoc.yml"""
        return self.convert(event_base64, outpath)


def main():
    """gistops entrypoint"""
    fire.Fire(GistOps)


if __name__ == '__main__':
    main()

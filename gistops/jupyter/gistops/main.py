#!/usr/bin/env python3
"""
Command line arguments for GistOps Operations
"""
import os
import logging
from pathlib import Path
from typing import List

import fire

import gists
import version
import nbconvertion


class GistOps():
    """gistops - Create static html reports from jupyter notebooks"""


    def __logs(self, logspath: Path, prefix: str='jupyter'):
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
      cwd: str = str(Path.cwd()), 
      logsdir: str = None ):

        self.__logs( logspath=Path(logsdir) if logsdir is not None else Path(cwd) )

        ############
        # Git Root #
        ############
        # Make git root current working directory 
        # and make path relative to git root
        self.__git_root = gists.assert_git_root(Path(cwd).resolve())
        # Important as gist.path is a unique key
        os.chdir(str(self.__git_root))


    def version(self) -> str:
        """Just print the version"""
        return version.__version__


    def convert(self, event_base64: str, outpath: str='.'):
        """Create static html reports from jupyter notebooks"""
        try:
            try:
                outpath = Path(outpath).resolve().relative_to(self.__git_root.resolve())
            except ValueError as err:
                raise gists.GistOpsError(
                  'output path MUST be sub directory of git root'
                  'in order to be accessable from downstream ops') from err

            try:
                if Path(event_base64).exists() and Path(event_base64).is_file():
                    with open(Path(event_base64), 'r', encoding='utf-8') as event_base64_file:
                        event_base64 = event_base64_file.read()
            except OSError:
                pass # e.g. filename to long for base64

            nbs: List[gists.Gist] = []
            for gist in gists.from_event(event_base64):
                if gist.path.suffix != '.ipynb':
                    continue # ... skip non .ipynb files

                try:
                    nbs.append( 
                      nbconvertion.convert(
                        gist = gist,
                        outpath = Path(outpath)) )

                    logging.getLogger('gistops.trail').info(f'{gist.path},converted')

                except Exception as err:
                    logging.getLogger('gistops.trail').error(f'{gist.path},convertion failed')
                    raise err
                
            return gists.to_event( nbs )
      
        except Exception as err:
            logging.getLogger('gistops.trail').error('*,unexpected error')
            logging.getLogger().error(str(err))
            raise err


    def run(self, event_base64: str, outpath: str='.') -> str:
        """Create static html reports from jupyter notebooks"""

        return self.convert(event_base64=event_base64, outpath=outpath)


def main():
    """gistops entrypoint"""
    fire.Fire(GistOps)


if __name__ == '__main__':
    main()

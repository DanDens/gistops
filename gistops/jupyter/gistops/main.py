#!/usr/bin/env python3
"""
Command line arguments for GistOps Operations
"""
import os
import logging
from pathlib import Path
from typing import List, Union

import fire

import gists
import version
import extract


class GistOps():
    """gistops - Extract static reports from jupyter notebooks"""


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


    def __init__(self, cwd: str = str(Path.cwd())):

        ############
        # Git Root #
        ############
        # Make git root current working directory 
        # and make path relative to git root
        self.__git_root = gists.assert_git_root(Path(cwd).resolve())
        # Important as gist.path is a unique key
        os.chdir(str(self.__git_root))

        self.__gistops_path = self.__git_root.joinpath('.gistops')
        self.__gistops_path.mkdir(parents=True, exist_ok=True)
        self.__logs( logspath=self.__gistops_path )


    def version(self) -> str:
        """Just print the version"""
        return version.__version__


    def extract(self, 
      event_base64: Union[str,list], 
      outpath: str = '.gistops/data'):
        """Extract static reports from jupyter notebooks"""

        try:
            if isinstance(event_base64, list):
                eb64s = event_base64
            elif isinstance(event_base64, str):
                eb64s = [event_base64] 
            else:
                raise gists.GistOpsError(
                  'event_base64 must bei either single base64 encoded event ' 
                  'or list of base64 encoded events')

            try:
                outpath = Path(outpath).resolve().relative_to(self.__git_root.resolve())
            except ValueError as err:
                raise gists.GistOpsError(
                  'output path MUST be sub directory of git root'
                  'in order to be accessable from downstream ops') from err

            nbs: List[gists.Gist] = []
            for eb64 in eb64s:
                try:
                    if Path(eb64).exists() and Path(eb64).is_file():
                        with open(Path(eb64), 'r', encoding='utf-8') as event_base64_file:
                            eb64 = event_base64_file.read()
                except OSError:
                    pass # e.g. filename to long for base64

                
                for gist in gists.from_event(eb64):
                    if gist.path.suffix != '.ipynb':
                        continue # ... skip non .ipynb files

                    try:
                        # Check if gist is already relative to outpath
                        try:
                            gist.path.relative_to(Path(outpath))
                            gist_outpath=Path('.')
                        except ValueError:
                            gist_outpath=Path(outpath)

                        nbs.extend( extract.extract(
                          gist = gist,
                          outpath = gist_outpath) )

                        logging.getLogger('gistops.trail').info(f'{gist.path},converted')

                    except Exception as err:
                        logging.getLogger('gistops.trail').error(f'{gist.path},convertion failed')
                        raise err
                    
            return gists.to_event( nbs )
      
        except Exception as err:
            logging.getLogger('gistops.trail').error('*,unexpected error')
            logging.getLogger().error(str(err))
            raise err


    def run(self, 
      event_base64: Union[str,list],
      outpath: str = '.gistops/data') -> str:
        """Extract static reports from jupyter notebooks"""

        return self.extract(
            event_base64=event_base64, 
            outpath=outpath)


def main():
    """gistops entrypoint"""
    fire.Fire(GistOps)


if __name__ == '__main__':
    main()

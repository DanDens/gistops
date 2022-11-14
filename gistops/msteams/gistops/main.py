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
import graph
import version


class GistOps():
    """gistops - msteams notification"""


    def __init__(self, cwd: str = str( Path.cwd() )):

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
        # Make git root current working directory 
        # and make path relative to git root
        self.__git_root = gists.assert_git_root(
          Path(cwd).resolve())
        # Important as gist.path is a unique key
        os.chdir(str(self.__git_root)) 


    def version(self) -> str:
        """Just print the version"""
        return version.__version__


    def report(self, 
      webhook_url: str=os.environ.get('GISTOPS_MSTEAMS_WEBHOOK_URL', None), 
      logsdir: str=str(Path.cwd())):
        """Report status to msteams webhook"""

        # Todo: read gistops.logs and gists.json
        # gistops_logs_path = Path(logsdir).joinpath('gistops.logs')

        gsts: List[gists.Gist] = gists.from_file(
          gists_json_path=Path(logsdir).joinpath('gists.json') )

        nxg = graph.as_graph(gsts)


    def run(self, 
      webhook_url: str=os.environ.get('GISTOPS_MSTEAMS_WEBHOOK_URL', None), 
      logsdir: str=str(Path.cwd())) -> str:
        """Report status to msteams webhook"""
        return self.report(
          webhook_url=webhook_url,
          logsdir=logsdir)


def main():
    """gistops entrypoint"""
    fire.Fire(GistOps)


if __name__ == '__main__':
    main()

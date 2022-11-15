#!/usr/bin/env python3
"""
Command line arguments for GistOps Operations
"""
import os
import logging
from pathlib import Path

import fire

import gists
import trails
import reporting
import version


class GistOps():
    """gistops - msteams notification"""


    def __init__(self, 
      cwd: str = str(Path.cwd()),
      logsdir: str = None ):

        logspath = Path(logsdir) if logsdir is not None else Path(cwd)
        logspath.mkdir(parents=True, exist_ok=True)
        datefmt='%Y-%m-%dT%H:%M:%SZ'

        self.__logspath=logspath

        # Logs to gistops.log
        logger = logging.getLogger()
        logfile = logging.FileHandler(
          logspath.joinpath('gistops.log'))
        logfile.setFormatter(logging.Formatter(
            'msteams,%(levelname)s,%(asctime)s,%(message)s', datefmt=datefmt ))
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
      webhook_url: str=None, 
      report_title: str=None):
        """Report status to msteams channel"""

        if webhook_url is None: 
            webhook_url=os.environ['GISTOPS_MSTEAMS_WEBHOOK_URL']
        if report_title is None:
            report_title=os.environ['GISTOPS_MSTEAMS_REPORT_TITLE']

        reporting.report(
          webhook_api = reporting.to_webhook_api(webhook_url), 
          report_title=report_title,
          gsts=gists.from_file(gists_json_path=self.__logspath.joinpath('gists.json')), 
          traillogs=trails.from_file(self.__logspath.joinpath('gistops.trail')) )


    def run(self, 
      webhook_url: str=None, 
      report_title: str=None) -> str:
        """Report status to msteams channel"""
        return self.report(
          webhook_url=webhook_url,
          report_title=report_title)


def main():
    """gistops entrypoint"""
    fire.Fire(GistOps)


if __name__ == '__main__':
    main()

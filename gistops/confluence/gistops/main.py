#!/usr/bin/env python3
"""
Command line arguments for GistOps Operations
"""
import os
import logging
from pathlib import Path

import fire

import gists
import publishing
import version


class GistOps():
    """gistops - Publish gists as pages to Confluence"""


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
        self.__dry_run = dry_run


    def version(self) -> str:
        """Just print the version"""
        return version.__version__


    def publish(self,
      event_base64: str,
      confluence_url: str = None,
      confluence_page_id: str = None,
      confluence_username: str = None,
      confluence_password: str = None):
        """Publish gist as page on confluence"""

        if confluence_url is None: 
            confluence_url=os.environ['GISTOPS_CONFLUENCE_URL']
        if confluence_page_id is None: 
            confluence_page_id=os.environ['GISTOPS_CONFLUENCE_PAGE_ID']
        if confluence_username is None:
            confluence_username=os.environ.get('GISTOPS_CONFLUENCE_USERNAME', None)
        if confluence_password is None:
            confluence_password=os.environ.get('GISTOPS_CONFLUENCE_PASSWORD', None)

        cnfl = publishing.connect_to_api(
          confluence_url, confluence_username, confluence_password )

        for gist in gists.from_event(event_base64):
            publishing.publish(
              cnfl = cnfl,
              gist = gist,
              confluence_page_id = confluence_page_id,
              dry_run = self.__dry_run)


    def run(self,
      event_base64: str,
      confluence_url: str = None,
      confluence_page_id: str = None,
      confluence_username: str = None,
      confluence_password: str = None) -> str:
        """Publish gist as page on confluence"""

        return self.publish(
          event_base64=event_base64,
          confluence_url=confluence_url,
          confluence_page_id=confluence_page_id,
          confluence_username=confluence_username,
          confluence_password=confluence_password)


def main():
    """gistops entrypoint"""
    fire.Fire(GistOps)


if __name__ == '__main__':
    main()

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

        datefmt='%Y-%m-%dT%H:%M:%SZ'

        # Logs to gistops.log
        logger = logging.getLogger()
        logfile = logging.FileHandler(
          Path(cwd).joinpath('gistops.log'))
        logfile.setFormatter(logging.Formatter(
            'confluence,%(levelname)s,%(asctime)s,%(message)s', datefmt=datefmt ))
        logger.addHandler(logfile)
        logger.setLevel(os.environ.get('LOG_LEVEL','INFO'))
        logger.info(version.__version__)

        # Trailing to gistops.trail
        traillog = logging.getLogger('gistops.trail')
        traillogfile = logging.FileHandler(
          Path(cwd).joinpath('gistops.trail'))
        traillogfile.setFormatter(logging.Formatter(
            'confluence,%(levelname)s,%(asctime)s,%(message)s', datefmt=datefmt ))
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
        self.__dry_run = dry_run


    def version(self) -> str:
        """Just print the version"""
        return version.__version__


    def publish(self,
      event_base64: str,
      confluence_url: str = None,
      confluence_username: str = None,
      confluence_password: str = None):
        """Publish gist as page on confluence"""

        try:
            if confluence_url is None: 
                confluence_url=os.environ['GISTOPS_CONFLUENCE_URL']
            if confluence_username is None:
                confluence_username=os.environ.get('GISTOPS_CONFLUENCE_USERNAME', None)
            if confluence_password is None:
                confluence_password=os.environ.get('GISTOPS_CONFLUENCE_PASSWORD', None)

            cnfl = publishing.connect_to_api(
              confluence_url, confluence_username, confluence_password )

            for gist in sorted(
              gists.from_event(event_base64),
              key=lambda g: 0 if g.path.suffix == '.jira' else 1 ):
                try:
                    publishing.publish(cnfl = cnfl, gist = gist, dry_run = self.__dry_run)

                    logging.getLogger('gistops.trail').info(
                      f'{gist.gist.path},published on {cnfl.url} as {gist.path.suffix}')
                except Exception as err:
                    logging.getLogger('gistops.trail').error(
                      f'{gist.gist.path},publishing on {cnfl.url} as {gist.path.suffix} failed')
                    raise err

        except Exception as err:
            logging.getLogger('gistops.trail').error('*,unexpected error')
            logging.getLogger().error(str(err))
            raise err


    def run(self,
      event_base64: str,
      confluence_url: str = None,
      confluence_username: str = None,
      confluence_password: str = None) -> str:
        """Publish gist as page on confluence"""

        return self.publish(
          event_base64=event_base64,
          confluence_url=confluence_url,
          confluence_username=confluence_username,
          confluence_password=confluence_password)


def main():
    """gistops entrypoint"""
    fire.Fire(GistOps)


if __name__ == '__main__':
    main()

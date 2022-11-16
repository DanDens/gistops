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


    def __logs(self, logspath: Path, prefix: str='confluence'):
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
      logsdir: str = None,
      dry_run: bool = False ):

        self.__logs( logspath=Path(logsdir) if logsdir is not None else Path(cwd) )

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


    def __cnfl_api(self,
      confluence_url: str = None,
      confluence_access_token: str = None,
      confluence_username: str = None,
      confluence_password: str = None) -> publishing.ConfluenceAPI:

        if confluence_url is None: 
            confluence_url=os.environ['GISTOPS_CONFLUENCE_URL']

        if confluence_access_token is None or confluence_access_token == '':
            confluence_access_token=os.environ.get('GISTOPS_CONFLUENCE_ACCESS_TOKEN', None)
        if confluence_access_token is not None and confluence_access_token != '':
            return publishing.connect_to_api( 
              confluence_url, confluence_access_token )

        if confluence_username is None or confluence_username == '':
            confluence_username=os.environ.get('GISTOPS_CONFLUENCE_USERNAME', None)
        if confluence_password is None or confluence_password == '':
            confluence_password=os.environ.get('GISTOPS_CONFLUENCE_PASSWORD', None)

        if confluence_username is not None and confluence_username != '' and  \
            confluence_password is not None and confluence_password != '':
            return publishing.connect_to_api_via_password( 
              confluence_url, confluence_username, confluence_password )

        raise gists.GistOpsError(
          'No credentials provided to authenticate with jira server, '
          'please provide either GISTOPS_CONFLUENCE_ACCESS_TOKEN or '
          'GISTOPS_CONFLUENCE_USERNAME and GISTOPS_CONFLUENCE_PASSWORD combination' )


    def publish(self,
      event_base64: str,
      confluence_url: str = None,
      confluence_access_token: str = None,
      confluence_username: str = None,
      confluence_password: str = None):
        """Publish gist as page on confluence"""

        try:
            cnfl = self.__cnfl_api( 
              confluence_url=confluence_url, 
              confluence_access_token=confluence_access_token, 
              confluence_username=confluence_username, 
              confluence_password=confluence_password )

            try:
                if Path(event_base64).exists() and Path(event_base64).is_file():
                    with open(Path(event_base64), 'r', encoding='utf-8') as event_base64_file:
                        event_base64 = event_base64_file.read()
            except OSError:
                pass # e.g. filename to long for base64

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
      confluence_access_token: str = None,
      confluence_username: str = None,
      confluence_password: str = None) -> str:
        """Publish gist as page on confluence"""

        return self.publish(
          event_base64=event_base64,
          confluence_url=confluence_url,
          confluence_access_token=confluence_access_token,
          confluence_username=confluence_username,
          confluence_password=confluence_password)


def main():
    """gistops entrypoint"""
    fire.Fire(GistOps)


if __name__ == '__main__':
    main()

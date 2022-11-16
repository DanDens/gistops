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
            'jira,%(levelname)s,%(asctime)s,%(message)s', datefmt=datefmt ))
        logger.addHandler(logfile)
        logger.setLevel(os.environ.get('LOG_LEVEL','INFO'))
        logger.info(version.__version__)

        # Trailing to gistops.trail
        traillog = logging.getLogger('gistops.trail')
        traillogfile = logging.FileHandler(
          logspath.joinpath('gistops.trail'))
        traillogfile.setFormatter(logging.Formatter(
            'jira,%(levelname)s,%(asctime)s,%(message)s', datefmt=datefmt ))
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


    def __jira_api(self,
      jira_url: str = None,
      jira_access_token: str = None,
      jira_username: str = None,
      jira_password: str = None) -> publishing.JiraAPI:

        if jira_url is None: 
            jira_url=os.environ['GISTOPS_JIRA_URL']

        if jira_access_token is None:
            jira_access_token=os.environ.get('GISTOPS_JIRA_ACCESS_TOKEN', None)
        if jira_access_token is not None:
            return publishing.connect_to_api( 
              jira_url, jira_access_token )
        else:
            if jira_username is None:
                jira_username=os.environ.get('GISTOPS_JIRA_USERNAME', None)
            if jira_password is None:
                jira_password=os.environ.get('GISTOPS_JIRA_PASSWORD', None)

            return publishing.connect_to_api_via_password( 
              jira_url, jira_username, jira_password )


    def publish(self,
      event_base64: str,
      jira_url: str = None,
      jira_access_token: str = None,
      jira_username: str = None,
      jira_password: str = None):
        """Publish gist as ticket description on jira"""
        try:
            jira = self.__jira_api(jira_url, jira_access_token, jira_username, jira_password)

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
                    publishing.publish(jira = jira, gist = gist, dry_run = self.__dry_run)

                    logging.getLogger('gistops.trail').info(
                      f'{gist.gist.path},published on {jira.url} as {gist.path.suffix}')
                except Exception as err:
                    logging.getLogger('gistops.trail').error(
                      f'{gist.gist.path},publishing on {jira.url} as {gist.path.suffix} failed')
                    raise err

        except Exception as err:
            logging.getLogger('gistops.trail').error('*,unexpected error')
            logging.getLogger().error(str(err))
            raise err


    def run(self,
      event_base64: str,
      jira_url: str = None,
      jira_access_token: str = None,
      jira_username: str = None,
      jira_password: str = None) -> str:
        """Publish gist as ticket description on jira"""

        return self.publish(
          event_base64=event_base64,
          jira_url=jira_url,
          jira_access_token=jira_access_token,
          jira_username=jira_username,
          jira_password=jira_password)


def main():
    """gistops entrypoint"""
    fire.Fire(GistOps)


if __name__ == '__main__':
    main()

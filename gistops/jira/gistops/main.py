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
      jira_url: str = None,
      jira_username: str = None,
      jira_password: str = None):
        """Publish gist as ticket description on jira"""

        if jira_url is None: 
            jira_url=os.environ['GISTOPS_JIRA_URL']
        if jira_username is None:
            jira_username=os.environ.get('GISTOPS_JIRA_USERNAME', None)
        if jira_password is None:
            jira_password=os.environ.get('GISTOPS_JIRA_PASSWORD', None)

        jira = publishing.connect_to_api(
          jira_url, jira_username, jira_password )

        for gist in sorted(
          gists.from_event(event_base64),
          key=lambda g: 0 if g.path.suffix == '.jira' else 1 ):
            publishing.publish(jira = jira, gist = gist, dry_run = self.__dry_run)


    def run(self,
      event_base64: str,
      jira_url: str = None,
      jira_username: str = None,
      jira_password: str = None) -> str:
        """Publish gist as ticket description on jira"""

        return self.publish(
          event_base64=event_base64,
          jira_url=jira_url,
          jira_username=jira_username,
          jira_password=jira_password)


def main():
    """gistops entrypoint"""
    fire.Fire(GistOps)


if __name__ == '__main__':
    main()
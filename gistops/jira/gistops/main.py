#!/usr/bin/env python3
"""
Command line arguments for GistOps Operations
"""
import os
import logging
from pathlib import Path
from typing import Union, List

import fire

import gists
import publishing
import version


class GistOps():
    """gistops - Publish gists as pages to Confluence"""


    def __logs(self, logspath: Path, prefix: str='jira'):
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
      dry_run: bool = False ):

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

        if jira_access_token is None or jira_access_token == '':
            jira_access_token=os.environ.get('GISTOPS_JIRA_ACCESS_TOKEN', None)
        if jira_access_token is not None and jira_access_token != '':
            return publishing.connect_to_api( 
              jira_url, jira_access_token )
        
        if jira_username is None or jira_username == '':
            jira_username=os.environ.get('GISTOPS_JIRA_USERNAME', None)
        if jira_password is None or jira_password == '':
            jira_password=os.environ.get('GISTOPS_JIRA_PASSWORD', None)

        if jira_username is not None and jira_username != '' and  \
            jira_password is not None and jira_password != '':
            return publishing.connect_to_api_via_password( 
              jira_url, jira_username, jira_password )

        raise gists.GistOpsError(
          'No credentials provided to authenticate with jira server, '
          'please provide either GISTOPS_JIRA_ACCESS_TOKEN or '
          'GISTOPS_JIRA_USERNAME and GISTOPS_JIRA_PASSWORD combination' )


    def publish(self,
      event_base64: Union[str,list],
      jira_url: str = None,
      jira_access_token: str = None,
      jira_username: str = None,
      jira_password: str = None):
        """Publish gist as ticket description on jira"""
        try:
            if isinstance(event_base64, list):
                eb64s = event_base64
            elif isinstance(event_base64, str):
                eb64s = [event_base64] 
            else:
                raise gists.GistOpsError(
                  'event_base64 must bei either single base64 encoded event ' 
                  'or list of base64 encoded events')

            jira = self.__jira_api(jira_url, jira_access_token, jira_username, jira_password)

            failed: List(str) = []
            for eb64 in eb64s:
                try:
                    if Path(eb64).exists() and Path(eb64).is_file():
                        with open(Path(eb64), 'r', encoding='utf-8') as event_base64_file:
                            eb64 = event_base64_file.read()
                except OSError:
                    pass # e.g. filename to long for base64

                for gist in sorted(
                  gists.from_event(eb64),
                  key=lambda g: 0 if g.path.suffix == '.jira' else 1 ):
                    if not publishing.publish(
                      jira = jira, gist = gist, dry_run = self.__dry_run):
                        failed.append(gist.trace_id)

            if len(failed) > 0:
                raise gists.GistOpsError(
                  f'Failed to publish gists {failed}, see previous errors')

        except Exception as err:
            logging.getLogger('gistops.trail').error('*,unexpected error')
            logging.getLogger().error(err, exc_info=True)
            raise err


    def run(self,
      event_base64: Union[str,list],
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

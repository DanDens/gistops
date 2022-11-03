#!/usr/bin/env python3
"""
Functions to mirror branches for git remotes
"""
import logging
from dataclasses import dataclass

from atlassian import Confluence

import gists

@dataclass
class ConfluenceAPI:
    """Internal Confluence API representation"""
    url: str
    api: Confluence


def connect_to_api( url: str, username: str, password: str ) -> ConfluenceAPI:
    """Connect to confluence Web API"""
    return ConfluenceAPI(
      url=url, api=Confluence(url=url, username=username, password=password) )


def publish(
  cnfl: Confluence,
  gist: gists.ConvertedGist,
  confluence_page_id: str,
  dry_run: bool = False):
    """Force mirror branches matching the given regex"""
    logger = logging.getLogger()

    logger.info(
      'curl -u USERNAME:PASSWORD -X POST -H "X-Atlassian-Token: nocheck" '
      f'-F "file=@${gist.path}" -F "comment= Matches {gist.gist.commit_id} git commit id" '
      f'${cnfl.url}/rest/api/content/${confluence_page_id}/child/attachment')

    if dry_run:
        return

    cnfl.api.attach_file(
      str(gist.path), 
      page_id=confluence_page_id, 
      comment=f'Matches {gist.gist.commit_id} git commit id')



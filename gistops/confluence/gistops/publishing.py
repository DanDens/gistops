#!/usr/bin/env python3
"""
Functions to mirror branches for git remotes
"""
import re
import logging
from pathlib import Path
from typing import List
import urllib.parse
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


def __iterate_attachments(gist: gists.ConvertedGist, jira_wiki:str) -> List[Path]:
    attachs = []
    for attach in re.findall(r'!(.+)?(?=!)', jira_wiki, re.MULTILINE):
        for candidate in [dep.joinpath(urllib.parse.unquote( attach )) for dep in gist.deps]:
            if candidate.exists():
                attachs.append(candidate)
                break
    return attachs


def publish(
  cnfl: Confluence,
  gist: gists.ConvertedGist,
  confluence_page_id: str,
  dry_run: bool = False):
    """Force mirror branches matching the given regex"""
    logger = logging.getLogger()

    if dry_run:
        return

    # https://atlassian-python-api.readthedocs.io/confluence.html#page-actions
    # https://community.atlassian.com/t5/Confluence-questions/Insert-Confluence-Wiki-Markdown-via-API/qaq-p/667936

    # Load wiki ...
    with open(gist.path, 'r', encoding='utf-8') as jira_wiki_file:
        jira_wiki = jira_wiki_file.read()

    attachs: List[Path] = __iterate_attachments(gist, jira_wiki)

    # Upload page
    logger.info(
      'curl -u USERNAME:PASSWORD -X PUT -H '
      '"X-Atlassian-Token: nocheck" -H "Content-Type: application/json" '
      f'-d \'{{"id":"{confluence_page_id}","title":"{gist.title}",'
      f'"body":"...","representation":"wiki"}}\''
      f'{cnfl.url}/rest/api/content/{confluence_page_id}')

    page: dict = cnfl.api.update_or_create(
      parent_id=confluence_page_id, 
      title=gist.title, 
      body=jira_wiki,
      representation='wiki')

    # Upload Attachments 
    for attach in attachs:
        logger.info(
          'curl -u USERNAME:PASSWORD -X POST -H "X-Atlassian-Token: nocheck" '
          f'-F "file=@${attach}" '
          f'-F "name={urllib.parse.quote(attach.name)}" '
          f'-F "comment={gist.gist.commit_id}" '
          f'${cnfl.url}/rest/api/content/${page["id"]}/child/attachment')

        cnfl.api.attach_file(
            str(attach), 
            name=urllib.parse.quote(attach.name),
            page_id=page['id'], 
            comment=f'Matches {gist.gist.commit_id} git commit id')

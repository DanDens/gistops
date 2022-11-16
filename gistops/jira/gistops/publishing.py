#!/usr/bin/env python3
"""
Functions to mirror branches for git remotes
"""
import re
import logging
from pathlib import Path
from typing import List, Any
import urllib.parse
from functools import wraps
from dataclasses import dataclass 

from jsonschema import validate
from jsonschema.exceptions import ValidationError
from atlassian import Jira

import gists


@dataclass
class JiraAPI:
    """Internal Confluence API representation"""
    url: str
    api: Jira


def connect_to_api(url: str, access_token: str) -> JiraAPI:
    """Connect to jira Web API"""
    return JiraAPI(url=url, api=Jira(url=url, token=access_token) )


def __tagged(tag_name: str):
    def inner_tagged(func):
        @wraps(func)
        def decorator_func(*args, **kwargs) -> Any:
            logger = logging.getLogger()

            jira: JiraAPI = \
                args[0] if len(args) > 0 else kwargs['jira']

            gist: gists.ConvertedGist = \
                args[1] if len(args) > 0 else kwargs['gist']

            if tag_name not in gist.gist.tags:
                return # not ment to be published on confluence
            jira_tags = gist.gist.tags[tag_name]

            try:
                validate(instance=jira_tags, schema={
                  "type": "object",
                  "properties": {
                      "issue": {"type": "string"},
                      "host": {"type": "string"}
                  },
                  "required": ["issue","host"]
                })
            except ValidationError as err:
                raise gists.GistOpsError(
                  'Schema validation failed for tag confluence') from err

            parsed_url = urllib.parse.urlparse(jira.url)
            if parsed_url.hostname != jira_tags['host']:
                logger.info(
                  f'Skipping gist because hostname {jira_tags["host"]} '
                  f'does not match {parsed_url.hostname}')
                return 

            return func(*args, **kwargs)

        return decorator_func
    return inner_tagged


def __attach_to_issue(
  jira: Jira, issue_key: str, attachpath: Path, dry_run: bool):
    logger = logging.getLogger()
    logger.info(
      'curl -D- -u USERNAME:PASSWORD -X POST -H "X-Atlassian-Token: nocheck" '
      f'-F "file=@{{{attachpath}}}" '
      f'{jira.url}/rest/api/2/issue/{issue_key}/attachments')

    if dry_run:
        return # Do nothing, please ...

    jira.api.add_attachment(issue_key=issue_key, filename=str(attachpath))


def __iterate_attachments(gist: gists.ConvertedGist, jira_wiki:str) -> dict:
    attachs = {}
    for attach in re.findall(r'(?<=!)\S+(?=!)', jira_wiki):
        for candidate in [dep.joinpath(urllib.parse.unquote(attach)) for dep in gist.deps]:
            if candidate.exists():
                attachs[attach] = candidate
                break
    return attachs


def __update_issue_summary(jira: Jira, issue_key: str, gist: gists.ConvertedGist, dry_run: bool):
    logger = logging.getLogger()

    # https://atlassian-python-api.readthedocs.io/jira.html
    # https://developer.atlassian.com/server/jira/platform/rest-apis/

    # Open wiki ...
    with open(gist.path, 'r', encoding='utf-8') as jira_wiki_file:
        jira_wiki = jira_wiki_file.read()
    attachs: List[Path] = __iterate_attachments(gist, jira_wiki)

    # replace attach references to not include pathes
    for attachref, attachpath in attachs.items():
        jira_wiki = jira_wiki.replace( f'!{attachref}!', f'!{str(attachpath.name)}!' )

    # Upload issue description ...
    logger.info(
      'curl -u USERNAME:PASSWORD -X PUT -H '
      '"X-Atlassian-Token: nocheck" -H "Content-Type: application/json" '
      '-d \'{"fields":{"description","..."} }\''
      f'{jira.url}/rest/api/2/issue/{issue_key}')

    if not dry_run:
        jira.api.update_issue_field(issue_key, {'description': jira_wiki})

    # Upload Attachments 
    for attachpath in attachs.values():
        __attach_to_issue(
          jira=jira, issue_key=issue_key, attachpath=attachpath, dry_run=dry_run)


@__tagged('jira')
def publish(
  jira: Jira,
  gist: gists.ConvertedGist,
  dry_run: bool = False):
    """Update jira issue summary"""

    issue_key = gist.gist.tags['jira']['issue']

    if gist.path.suffix == '.jira':
        __update_issue_summary( 
          jira=jira, issue_key=issue_key, gist=gist, dry_run=dry_run )
    else:
        __attach_to_issue( 
          jira=jira, issue_key=issue_key, attachpath=gist.path, dry_run=dry_run )

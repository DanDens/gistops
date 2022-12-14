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


def connect_to_api_via_password(url: str, username: str, password: str) -> JiraAPI:
    """Connect to jira Web API"""
    return JiraAPI(
      url=url, api=Jira(url=url, username=username, password=password) )


def __tagged(tag_name: str):
    def inner_tagged(func):
        @wraps(func)
        def decorator_func(*args, **kwargs) -> Any:
            logger = logging.getLogger()

            jira: JiraAPI = \
                args[0] if len(args) > 0 else kwargs['jira']

            gist: gists.Gist = \
                args[1] if len(args) > 0 else kwargs['gist']

            if tag_name not in gist.tags:
                return # not ment to be published on confluence
            jira_tags = gist.tags[tag_name]

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


def __iterate_attachments(gist: gists.Gist, jira_wiki:str) -> dict:
    attachs = {}

    resource_paths: List[dict] = []
    for resource in gist.resources:
        if resource.rfind(':') < 0:
            continue # not a valid resource specifier
        
        resource_paths.append(
            {
                'parent': Path(resource.split(':')[0]),
                'pattern': resource.split(':')[-1]
            }
        )

    for attach in re.findall(
      pattern=r'(?<=!)\S+(?=[!\|])', string=jira_wiki, flags=re.MULTILINE):
        
        # Preprocess possible attach paths
        unquoted_attach_name = urllib.parse.unquote(attach)
        possible_attach_paths = []
        for resource_path in resource_paths:
            possible_attach_paths.append( resource_path['parent'].joinpath(unquoted_attach_name) )

        # Lookup files from resource paths
        for resource_path in resource_paths:
            resource_parent: Path = resource_path['parent']
            resource_pattern: str = resource_path['pattern']

            for candidate_path in resource_parent.glob(resource_pattern):
                if candidate_path in possible_attach_paths and \
                    candidate_path.is_file():
                    attachs[attach] = candidate_path
                    break # attachment found
            else:
                continue
            break # attachment found

    return attachs


def __update_issue_summary(jira: Jira, issue_key: str, gist: gists.Gist, dry_run: bool):
    logger = logging.getLogger()

    # https://atlassian-python-api.readthedocs.io/jira.html
    # https://developer.atlassian.com/server/jira/platform/rest-apis/

    # Open wiki ...
    with open(gist.path, 'r', encoding='utf-8') as jira_wiki_file:
        jira_wiki = jira_wiki_file.read()
    attachs: List[Path] = __iterate_attachments(gist, jira_wiki)

    # replace attach references to not include pathes
    for attachref, attachpath in attachs.items():
        logger.info(f'replacing "!{attachref}!" with "!{str(attachpath.name)}!"')
        jira_wiki = re.sub(
            pattern=fr'(?<=!){re.escape(attachref)}(?=[!\|])', 
            repl=attachpath.name, 
            string=jira_wiki, 
            flags=re.MULTILINE )

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
  gist: gists.Gist,
  dry_run: bool = False) -> bool:
    """Update jira issue summary"""

    issue_key = gist.tags['jira']['issue']
    try:
        if gist.path.suffix == '.jira':
            __update_issue_summary( 
              jira=jira, issue_key=issue_key, gist=gist, dry_run=dry_run )

            logging.getLogger('gistops.trail').info(
              f'{gist.trace_id},published as {gist.path.suffix} '
              f'description on issue {issue_key} on host {jira.url}')
        else:
            __attach_to_issue( 
            jira=jira, issue_key=issue_key, attachpath=gist.path, dry_run=dry_run )

            logging.getLogger('gistops.trail').info(
              f'{gist.trace_id},published as {gist.path.suffix} '
              f'attachment on issue {issue_key} on host {jira.url}')

    except Exception as err:
        what = 'description' if gist.path.suffix == '.jira' else 'attachment'

        logging.getLogger('gistops.trail').error(
          f'{gist.trace_id},publishing {what} as {gist.path.suffix} '
          f'on issue {issue_key} on {jira.url} failed')
        logging.getLogger().error(err, exc_info=True)
        return False 

    return True
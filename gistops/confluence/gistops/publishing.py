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
from atlassian import Confluence

import gists


@dataclass
class ConfluenceAPI:
    """Internal Confluence API representation"""
    url: str
    api: Confluence


def connect_to_api( url: str, access_token: str ) -> ConfluenceAPI:
    """Connect to confluence Web API"""

    return ConfluenceAPI(
      url=url, api=Confluence(url=url, token=access_token) )

def connect_to_api_via_password( url: str, username: str, password: str ) -> ConfluenceAPI:
    """Connect to confluence Web API"""

    return ConfluenceAPI(
      url=url, api=Confluence(url=url, username=username, password=password) )


def __tagged(tag_name: str):
    def inner_tagged(func):
        @wraps(func)
        def decorator_func(*args, **kwargs) -> Any:
            logger = logging.getLogger()

            cnfl: ConfluenceAPI = \
                args[0] if len(args) > 0 else kwargs['cnfl']

            gist: gists.Gist = \
                args[1] if len(args) > 0 else kwargs['gist']

            if tag_name not in gist.tags:
                return # not ment to be published on confluence
            cnfl_tags = gist.tags[tag_name]

            try:
                validate(instance=cnfl_tags, schema={
                  "type": "object",
                  "properties": {
                      "page": {"type": "string"},
                      "host": {"type": "string"}
                  },
                  "required": ["page","host"]
                })
            except ValidationError as err:
                raise gists.GistOpsError(
                  'Schema validation failed for tag confluence') from err

            parsed_url = urllib.parse.urlparse(cnfl.url)
            if parsed_url.hostname != cnfl_tags['host']:
                logger.info(
                  f'Skipping gist because hostname {cnfl_tags["host"]} '
                  f'does not match {parsed_url.hostname}')
                return 

            return func(*args, **kwargs)

        return decorator_func
    return inner_tagged


def __attach_to_page(
  page_id: str, attachpath: Path, cnfl: Confluence, gist: gists.Gist, dry_run: bool):
    logger = logging.getLogger()
    logger.info(
      'curl -u USERNAME:PASSWORD -X POST -H "X-Atlassian-Token: nocheck" '
      f'-F "file=@${attachpath}" '
      f'-F "name={attachpath.name}" '
      f'-F "comment={gist.commit_id}" '
      f'${cnfl.url}/rest/api/content/${page_id}/child/attachment')

    if dry_run:
        return # Do nothing, please ...

    cnfl.api.attach_file(
        str(attachpath), 
        name=attachpath.name,
        page_id=page_id, 
        comment=f'Matches {gist.commit_id} git commit id')


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

    for attach in re.findall(r'(?<=!)\S+(?=!)', jira_wiki):
        
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


def __update_page(parent_id: str, cnfl: Confluence, gist: gists.Gist, dry_run: bool) -> str:
    logger = logging.getLogger()

    # https://atlassian-python-api.readthedocs.io/confluence.html#page-actions
    # https://community.atlassian.com/t5/Confluence-questions/Insert-Confluence-Wiki-Markdown-via-API/qaq-p/667936

    # Open wiki ...
    with open(gist.path, 'r', encoding='utf-8') as jira_wiki_file:
        jira_wiki = jira_wiki_file.read()
    attachs: List[Path] = __iterate_attachments(gist, jira_wiki)

    # replace attach references to not include pathes
    for attachref, attachpath in attachs.items():
        logger.info(f'replacing "!{attachref}!" with "!{str(attachpath.name)}!"')
        jira_wiki = jira_wiki.replace( f'!{attachref}!', f'!{str(attachpath.name)}!' )

    # Upload page ...
    logger.info(
      'curl -u USERNAME:PASSWORD -X PUT -H '
      '"X-Atlassian-Token: nocheck" -H "Content-Type: application/json" '
      f'-d \'{{"id":"{parent_id}","title":"{gist.title}",'
      f'"body":"...","representation":"wiki"}}\''
      f'{cnfl.url}/rest/api/content/{parent_id}')

    if not dry_run:
        page: dict = cnfl.api.update_or_create(
          parent_id=parent_id, title=gist.title, body=jira_wiki, representation='wiki')
        page_id = page["id"]
    else: 
        space: str = cnfl.api.get_page_space(parent_id)
        page_id = cnfl.api.get_page_id(space, gist.title)

    # Upload Attachments 
    for attachpath in attachs.values():
        __attach_to_page(
          page_id=page_id, attachpath=attachpath, cnfl=cnfl, gist=gist, dry_run=dry_run)

    return page_id


@__tagged('confluence')
def publish(
  cnfl: Confluence,
  gist: gists.Gist,
  dry_run: bool = False) -> bool:
    """Force mirror branches matching the given regex"""

    parent_id = gist.tags['confluence']['page']

    try:
        if gist.path.suffix == '.jira':
            page_id = __update_page( 
              parent_id=parent_id,
              cnfl=cnfl,
              gist=gist,
              dry_run=dry_run )

            logging.getLogger('gistops.trail').info(
              f'{gist.trace_id},published page {page_id} '
              f'as {gist.path.suffix} on host {cnfl.url}')

        else:
            space: str = cnfl.api.get_page_space(parent_id)
            page_id = cnfl.api.get_page_id(space, gist.title)

            __attach_to_page(
              page_id=page_id,
              attachpath=gist.path,
              cnfl=cnfl,
              gist=gist,
              dry_run=dry_run )
        
            logging.getLogger('gistops.trail').info(
              f'{gist.trace_id},published attachment as {gist.path.suffix} '
              f'on page {page_id} on host {cnfl.url}')

    except Exception as err:
        what = 'page' if gist.path.suffix == '.jira' else 'attachment'

        logging.getLogger('gistops.trail').error(
          f'{gist.trace_id},publishing {what} as {gist.path.suffix} '
          f'below parent page {parent_id} on {cnfl.url} failed')
        logging.getLogger().error(err, exc_info=True)
        return False 

    return True

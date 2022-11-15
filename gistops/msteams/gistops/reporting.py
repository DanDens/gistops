#!/usr/bin/env python3
"""
Report Traillogs to msteams channel
"""
import json
import logging
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from collections import Counter
from typing import List

from jinja2 import BaseLoader, Environment

import trails
import gists


__TRAILLOG_TEMPLATE_J2 = '''
{%- if gists | length > 0 -%}
<table>
<tr><th>gist</th><th>actions</th></tr>
{%- for gist in gists -%}
<tr>
<td class="operation"><p style="color:#{{-traillevel_2_rgbcolor(gist.level)-}}";>
<tiny>{{- gist.prefix -}}</tiny><br />{{- gist.path -}}
</td>
</p><td class="action">
{%- for trail in gist.trails -%}
<p style="color:#{{-traillevel_2_rgbcolor(trail.level)-}}";>
{{- trail.operation }}: {{ trail.action -}}  
</p><br />
{%- endfor -%}
</td></tr>
{%- endfor -%}
</table>
{%- endif -%}
'''

def __as_j2_params(gsts: List[gists.Gist], traillogs: List[trails.TrailLog]) -> dict:
    ###################
    # Shared Prefixes #
    ###################
    # Count common path prefixes
    cnt = Counter()
    for gist in gsts:
        cnt.update(gist.path.parents)

    # Filter path prefixes which are not shared by gists
    shared_prefixes = [prefix for prefix, count in cnt.items() if count > 1]
    shared_prefixes = sorted(shared_prefixes, key= lambda prefix : len(str(prefix)), reverse=True)

    ###############
    # Sort Trails #
    ###############
    gist_trails= {}
    for trail in sorted(traillogs, key= lambda trail : trail.time):
        if trail.gist not in gist_trails:
            gist_trails[trail.gist] = []

        gist_trails[trail.gist].append({
          'operation': trail.operation,
          'level': trail.level,
          'action': trail.action
        }) 

    ################
    # Build Params #
    ################
    j2_params = {'gists': []}
    for gist in gsts:
        # Select longest shared prefix
        for prefix in shared_prefixes:
            try:
                path = gist.path.relative_to(prefix)
                break
            except ValueError:
                pass
        else:
            prefix = ''
            path = gist.path

        this_trails = gist_trails[gist.path] if gist.path in gist_trails else []

        this_level = logging.NOTSET
        if len(this_trails) > 0:
            max_trail: dict = max(this_trails, key=lambda trail: trail['level'])
            this_level = max_trail['level']

        j2_params['gists'].append({
          'prefix': prefix,
          'path': path,
          'level': this_level,
          'trails': this_trails })

    return j2_params


def __traillevel_2_rgbcolor( level: int ):
    match level:
        case logging.WARN: return 'fc7e05'
        case logging.ERROR: return 'fd6b6b'
        case logging.FATAL: return 'fd6b6b'
        case logging.CRITICAL: return 'fd6b6b'
        case _: return '000000'


def __as_html_report(gsts: List[gists.Gist], traillogs: List[trails.TrailLog]) -> str:
    pandoc_j2_env = Environment(loader=BaseLoader())
    pandoc_j2_env.globals['traillevel_2_rgbcolor'] = __traillevel_2_rgbcolor
    pandoc_j2_tmpl = pandoc_j2_env.from_string(__TRAILLOG_TEMPLATE_J2.replace('\n',''))
    return pandoc_j2_tmpl.render( __as_j2_params(gsts=gsts, traillogs=traillogs) )


class MsTeamsWebhookAPI:
    """Sends POST request to msteams webhook"""
    def __init__(self, url: str):
        self.__url = url


    def send(self, message_card: str):
        """Sends POST request to msteams webhook"""
        logger = logging.getLogger()
        try:
            logger.info(
              f"curl -X POST {self.__url} -H 'Content-Type: application/json' "
              f"-d '{message_card}'")
            req = Request(self.__url, message_card.encode('utf-8'))
            response = urlopen(req)
            response.read()
        except HTTPError as err:
            logger.error("Request failed: %d %s", err.code, err.reason)
            raise err
        except URLError as err:
            logger.error("Server connection failed: %s", err.reason)
            raise err


def to_webhook_api(url: str) -> MsTeamsWebhookAPI:
    """Create webhook api from url"""
    return MsTeamsWebhookAPI(url)


def report(
  webhook_api: MsTeamsWebhookAPI, 
  report_title: str,
  gsts: List[gists.Gist], 
  traillogs: List[trails.TrailLog]):
    """Sends a status report to msteams channel"""

    webhook_api.send( message_card=json.dumps({
      "@context": "https://schema.org/extensions",
      "@type": "MessageCard",
      "themeColor": __traillevel_2_rgbcolor(trails.max_severity(traillogs)),
      "title": report_title,
      "text": __as_html_report(gsts=gsts, traillogs=traillogs)
    }) )

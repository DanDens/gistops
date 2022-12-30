#!/usr/bin/env python3
"""
Gist Representation and Factories
"""
import json
import base64
from pathlib import Path
from dataclasses import dataclass
from typing import List

import semver
from jsonschema import validate

import version

##################
# EXPORTED TYPES #
##################
class GistOpsError(Exception):
    """ GistOps representation error """


@dataclass
class Gist:
    """ Gist representation """
    path: Path
    commit_id: str
    tags: dict
    resources: List[str]
    trace_id: Path
    title: str


def from_event(event_base64: str) -> List[Gist]:
    """ Read Gists Event """ 

    try:
        def __from_base64(event_base64: str) -> str:
            base64_bytes = event_base64.encode('ascii')
            message_bytes = base64.b64decode(base64_bytes)
            return message_bytes.decode('ascii')

        event: dict = json.loads(__from_base64(event_base64))
    except json.JSONDecodeError as err:
        raise GistOpsError('Invalid event') from err

    validate(instance=event, schema={
        "type": "object",
        "properties": {
            "semver": {"const": version.__semver__},
            "record-type": {"const": "Gist"},
            "records": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "commit_id": {"type": "string"},
                        "tags": {"type":"object"},
                        "resources": {
                            "type": "array",
                            "items": { "type": "string" }
                        },
                        "trace_id": {"type": "string"},
                        "title": {"type": "string"}
                    },
                    "required": ["path", "commit_id", "tags", "resources", "trace_id", "title"]
                }
            }
        },
        "required": ["semver","record-type","records"]
    })

    # Check major version 
    event_semver = semver.VersionInfo.parse(event['semver'])
    this_semver = semver.VersionInfo.parse(version.__semver__)
    if event_semver.major != this_semver.major:
        raise GistOpsError(
          f"Event semver major version differ {event['semver']} != {version.__semver__}")

    return [ Gist(
        Path(rec['path']), 
        rec['commit_id'], 
        rec['tags'], 
        rec['resources'], 
        Path(rec['trace_id']), 
        rec['title'] ) for rec in event['records'] ]


def __to_basic_dict(gist: Gist) -> dict:
    """Returns gist as dict using basic types"""
    return {
        'path': str(gist.path),
        'tags': gist.tags,
        'commit_id': gist.commit_id,
        'resources': gist.resources,
        'trace_id': str(gist.trace_id),
        'title': gist.title }


def to_event(gists: List[Gist]) -> str:
    """Returns gist as dict using basic types"""

    event = {
        "semver": version.__semver__,
        "record-type": 'Gist',
        "records": [__to_basic_dict(gist) for gist in gists] }

    validate(instance=event, schema={
    "type": "object",
        "properties": {
            "semver": {"const": version.__semver__},
            "record-type": {"const": "Gist"},
            "records": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "commit_id": {"type": "string"},
                        "tags": {"type":"object"},
                        "resources": {
                            "type": "array",
                            "items": { "type": "string" }
                        },
                        "trace_id": {"type": "string"},
                        "title": {"type": "string"}
                    },
                    "required": ["path", "commit_id", "tags", "resources", "trace_id", "title"]
                }
            }
        },
        "required": ["semver","record-type","records"]
    })

    def __to_base64(event_str: str) -> str:
        message_bytes = event_str.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        return base64_bytes.decode('ascii')

    return __to_base64(
      json.dumps(event, separators=(',',':')))


def j2_params(gist: Gist) -> dict:
    """Returns the gist as dict"""
    return {
      'name': str(gist.path.name),
      'dir': str(gist.path.parent),
      'stem': str(gist.path.stem),
      'suffix': str(gist.path.suffix),
      'parent': str(gist.path.parent.name),
      **__to_basic_dict(gist) }


######################
# EXPORTED FUNCTIONS #
######################
def assert_git_root(gist_absolute_path: Path) -> Path:
    """Locate git root directory from gist_path"""
    if not gist_absolute_path.exists():
        raise GistOpsError(f'{gist_absolute_path} does not exist')

    def traverse_upwards(gist_path: Path) -> Path:
        if gist_path == gist_path.parent:
            return None

        if gist_path.is_dir():
            if len(list(gist_path.glob('.git'))) == 1:
                return gist_path

        return traverse_upwards(gist_path.parent)

    git_root_path = traverse_upwards(gist_absolute_path.resolve())
    if not git_root_path:
        raise GistOpsError(
            f'{gist_absolute_path} is not in a git repository. '
            'Please run from valid git repository')

    return git_root_path

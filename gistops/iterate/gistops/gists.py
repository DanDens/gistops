#!/usr/bin/env python3
"""
Gist Representation and Factories
"""
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List
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


def to_event(gists: List[Gist]) -> str:
    """Returns gist as dict using basic types"""
        
    def __to_basic_dict(gist: Gist) -> dict:
        """Returns gist as dict using basic types"""
        return {
        'path': str(gist.path),
        'tags': gist.tags,
        'commit_id': gist.commit_id }
    
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
                        "tags": {"type":"object"}
                    },
                    "required": ["path","commit_id","tags"]
                }
            }
        },
        "required": ["semver","record-type","records"]
    })

    return json.dumps(json.dumps(event, separators=(',',':')))


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

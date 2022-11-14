#!/usr/bin/env python3
"""
Gist Representation and Factories
"""
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List

from jsonschema import validate


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


def from_file(gists_json_path: Path) -> List[Gist]:
    """ Read Gists from File """ 

    try:
        with open(gists_json_path, 'r', encoding='utf-8') as gists_json_file:
            gsts: list = json.loads(gists_json_file.read())
    except json.JSONDecodeError as err:
        raise GistOpsError('Invalid event') from err

    validate(instance=gsts, schema={
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
    })

    return [ Gist(Path(gist['path']), gist['commit_id'], gist['tags']) for gist in gsts ]


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

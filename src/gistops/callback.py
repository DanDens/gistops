#!/usr/bin/env python3
"""
Functions to publish gists
"""
import json
from pathlib import Path
from typing import Any, List, Callable
from functools import wraps
from jsonschema import validate

import gists


def __parametrized(func):
    @wraps(func)
    def decorator_func(*args, **kwargs) -> Any:
        gist: gists.Gist = \
             args[1] if len(args) > 0 else kwargs['gist']
        if 'publish' not in gist.ops:
            return None # ok, not all gists are rendered

        # Validate pandoc parameters
        validate(instance=gist.ops['publish'], schema={
            "type": "object",
            "description":"Callback information",
            "properties": {
                "callback" : {"type" : "string", "description": "Path to executable"},
                "args" : {
                    "type" : "array", 
                    "description": "Extra arguments to pass on to executable",
                    "items": { "type": "string" }
                }
            },
            "required":["callback"]
        })

        callback_path = Path(gist.ops['publish']['callback'])

        # Double check output path inside git
        try:
            callback_path.resolve().relative_to(gist.root)
        except ValueError as err:
            raise gists.GistError(
              f'Unexcepted output path {callback_path.resolve()}; ' 
              f'must be relative to git root {gist.root.resolve()}') from err

        if not callback_path.exists():
            raise gists.GistError(f"executable {gist.ops['publish']['callback']} does not exist")
             
        return func(*args, **kwargs)

    return decorator_func


@__parametrized
def publish(
  shrun: Callable[[List[str]], str], 
  gist: gists.Gist, 
  dry_run: bool = False):
    """Converts gist using pandoc as configured by .gitattributes""" 

    cmd=[ 
      f'"{str(gist.root.joinpath(gist.ops["publish"]["callback"]))}"', 
      f'"{str(gist.path)}"', 
      json.dumps(json.dumps(gist.ops,separators=(',', ':'))) ]
    if 'args' in gist.ops["publish"]:
        cmd=cmd.extend(gist.ops["publish"]['args'])

    shrun(cmd=cmd, do_not_execute=dry_run)

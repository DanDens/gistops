#!/usr/bin/env python3
"""
Functions to publish gists
"""
import json
from pathlib import Path
from typing import Any, List, Callable
from functools import wraps
from jsonschema import validate
from gistops.gists import Gist, GistError


def __parametrized(func):
    @wraps(func)
    def decorator_func(*args, **kwargs) -> Any:
        gist: Gist = \
             args[1] if len(args) > 0 else kwargs['gist']
        if 'publish' not in gist.ops:
            return None # ok, not all gists are rendered

        # Validate pandoc parameters
        validate(instance=gist.ops['publish'], schema={
          "type" : "object",
          "description": "Publish Configuration",
          "properties": {
              "callbacks":{
                  "type":"array",
                  "description":"Ordered array of publishing functions called for each gist",
                  "items": {
                      "type": "object",
                      "description":"Callback information",
                      "properties": {
                          "exe" : {"type" : "string", "description": "Path to executable"},
                          "args" : {
                              "type" : "array", 
                              "description": "Extra arguments to pass on to executable",
                              "items": { "type": "string" }
                          }
                      },
                      "required":["exe"]
                  }
              }
          },
          "required":["callbacks"]
        })

        for callback in gist.ops['publish']['callbacks']:
            if not Path(callback['exe']).exists():
                raise GistError(f"executable {callback['exe']} does not exist")

        return func(*args, **kwargs)

    return decorator_func


@__parametrized
def publish(
  shrun: Callable[[List[str]], str], 
  gist: Gist, 
  dry_run: bool = False):
    """Converts gist using pandoc as configured by .gitattributes""" 
    
    for callback in gist.ops['publish']['callbacks']:
        cmd=[ 
          f'"{str(gist.root.joinpath(callback["exe"]))}"', 
          f'"{str(gist.path)}"', 
          json.dumps(json.dumps(gist.ops,separators=(',', ':'))) ]
        if 'args' in callback:
            cmd=cmd.extend(callback['args'])
            
        shrun(cmd=cmd, do_not_execute=dry_run)
            
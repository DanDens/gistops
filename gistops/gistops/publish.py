#!/usr/bin/env python3
import logging
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
        
        for cb in gist.ops['publish']['callbacks']:
            if not Path(cb['exe']).exists():
                raise GistError(f"executable {cb['exe']} does not exist")
                
        return func(*args, **kwargs)
            
    return decorator_func


@__parametrized
def publish(shrun: Callable[[List[str]], str], gist: Gist):
    """Converts gist using pandoc as configured by .gitattributes""" 
    logger = logging.getLogger()
    
    for cb in gist.ops['publish']['callbacks']:
        cmd=[ str(gist.root.joinpath(cb['exe'])), str(gist.path), str(json.dumps(gist.ops)) ]
        if 'args' in cb:
            cmd=cmd.extend(cb['args'])
            
        for cb in gist.ops['publish']['callbacks']:
            shrun(cmd)
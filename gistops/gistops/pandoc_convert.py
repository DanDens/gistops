#!/usr/bin/env python3
import logging
from pathlib import Path
from typing import Any, List, Callable, NamedTuple, List
from functools import wraps
from jsonschema import validate
from gistops.gists import Gist


def __parametrized(func):
    @wraps(func)
    def decorator_func(*args, **kwargs) -> Any:
        
        gist: Gist = \
             args[1] if len(args) > 0 else kwargs['gist']
             
        # Validate pandoc parameters
        validate(instance=gist.ops, schema={
          "type" : "object",
          "properties" : {
            "type" : {"const" : "markdown", "description": "Gist type, currently only markdown is supported"},
            "pandoc": {
              "type" : "object",
              "description": "Pandoc Configuration",
              "properties": {
                  "format":{"const":"pdf","description":"Output Format, only pdf supported"},
                  "config":{"type":"string","description":"Pandoc configuration file path"},
                  "outfile":{"type":"string","description":"Output file path"}
              },
              "required":["format","config","outfile"]
            }
          },
          "required":["type"]
        })
        
        if 'pandoc' not in gist.ops:
            return None # ok, not all files are rendered

        assert(Path(gist.ops['pandoc']['config']).exists())

        return func(*args, **kwargs)
            
    
    return decorator_func


@__parametrized
def convert_gist(shrun: Callable[[List[str],bool], str], gist: Gist):
    """Converts gist using pandoc as configured by .gitattributes""" 
    logger = logging.getLogger()
    logger.info(f'> {gist.path}')
    
    # Clean rendered output
    outpath = Path(gist.ops['pandoc']['outfile'])
    if outpath.exists():
        outpath.unlink()
        
    shrun(cmd=[
      'pandoc',str(gist.path),
      '-f',gist.ops['type'],
      '-t',gist.ops['pandoc']['format'],
      '-d',gist.ops['pandoc']['config'],
      '-o',gist.ops['pandoc']['outfile'],
      f'--resource-path={gist.path.parent}'])
    
    
    
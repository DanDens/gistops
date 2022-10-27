#!/usr/bin/env python3
import logging
from pathlib import Path
from typing import Any, List, Callable
from functools import wraps
from jsonschema import validate
from gistops.gists import Gist, GistError
from gistops.shell import ShellError


def __git_ignore_output(shrun: Callable[[List[str]], str], gist: Gist): 
    logger = logging.getLogger()
    
    outfile_path: Path = Path(gist.ops['render']['outfile'])
    try:
      shrun(cmd=['git','check-ignore','--quiet',str(outfile_path)])
      return # already ignored
    except ShellError as _:
      pass
      
    # Ignore output file locally
    gitignore_path: Path = gist.path.parent.joinpath('.gitignore')
    with open(gitignore_path, 'a+') as gitignore_file:
      gitignore_file.write(f'\n{outfile_path.name}')
      


def __parametrized(func):
    @wraps(func)
    def decorator_func(*args, **kwargs) -> Any:
        
        gist: Gist = \
             args[1] if len(args) > 0 else kwargs['gist']
        if 'render' not in gist.ops:
            return None # ok, not all gists are rendered
            
        # Validate pandoc parameters
        validate(instance=gist.ops['render'], schema={
          "type" : "object",
          "description": "Pandoc Configuration",
          "properties": {
              "format":{"const":"pdf","description":"Output Format, only pdf supported"},
              "config":{"type":"string","description":"Pandoc configuration file path"},
              "outfile":{"type":"string","description":"Output file path"},
              "git-ignore":{"type":"boolean","description":"Ensure output file is ignored"}
          },
          "required":["format","config","outfile"]
        })
        
        if not Path(gist.ops['render']['config']).exists():
            raise GistError(f"{gist.ops['render']['config']} does not exist")

        return func(*args, **kwargs)
            
    return decorator_func


@__parametrized
def render(shrun: Callable[[List[str]], str], gist: Gist):
    """Converts gist using pandoc as configured by .gitattributes""" 
    logger = logging.getLogger()
    
    # Clean rendered output
    outpath = Path(gist.ops['render']['outfile'])
    if outpath.exists():
        outpath.unlink()
    
    if 'git-ignore' in gist.ops['render'] and gist.ops['render']['git-ignore']:
      __git_ignore_output(shrun=shrun, gist=gist)
     
    shrun(cmd=[
      'pandoc',str(gist.path),
      '-f',gist.ops['type'],
      '-t',gist.ops['render']['format'],
      '-d',gist.ops['render']['config'],
      '-o',gist.ops['render']['outfile'],
      f'--resource-path={gist.path.parent}'])
    




#!/usr/bin/env python3
import logging
from pathlib import Path
from typing import Any, List, Callable
from functools import wraps
from jsonschema import validate
from gistops.gists import Gist, GistError
from gistops.shell import ShellError


def __git_ignore_output(
  shrun: Callable[[List[str]], str], 
  gist: Gist,
  dry_run: bool): 
    logger = logging.getLogger()
    
    output_path: Path = Path(gist.ops['render']['output'])
    try:
      # https://git-scm.com/docs/git-check-ignore
      shrun(cmd=['git','check-ignore','--quiet',str(output_path)])
      return # already ignored
    except ShellError as _:
      pass
    
    if dry_run:
      return # Do nothing, please ...
      
    # Ignore output file locally
    gitignore_path: Path = gist.path.parent.joinpath('.gitignore')
    with open(gitignore_path, 'a+') as gitignore_file:
      gitignore_file.write(f'\n{output_path.name}')
      


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
          "description": "Selection of Pandoc Configuration Parameters, see https://pandoc.org/MANUAL.html",
          "properties": {
              "from":{"type":"string","description":"Input Format, see -f option or --from=FORMAT"},
              "to":{"type":"string","description":"Output Format, see -t option or --to=FORMAT"},
              "defaults":{"type":"string","description":"Pandoc configuration file path, see --defaults=FILE"},
              "output":{"type":"string","description":"Output file path, see --output=FILE"},
              "git-ignore":{"type":"boolean","description":"Ensure output file is ignored. If true adds file to .gitignore"}
          },
          "required":["from","to","defaults","output"]
        })
        
        if not Path(gist.ops['render']['defaults']).exists():
            raise GistError(f"{gist.ops['render']['defaults']} does not exist")

        return func(*args, **kwargs)
            
    return decorator_func


@__parametrized
def render(
  shrun: Callable[[List[str]], str], 
  gist: Gist, 
  dry_run: bool = False):
    """Converts gist using pandoc as configured by .gitattributes""" 
    logger = logging.getLogger()
    
    
    if 'git-ignore' in gist.ops['render'] and gist.ops['render']['git-ignore']:
      __git_ignore_output(shrun=shrun, gist=gist, dry_run=dry_run)
     
    # Clean rendered output
    if not dry_run:
      outpath = Path(gist.ops['render']['output'])
      if outpath.exists():
          outpath.unlink()
     
    shrun(cmd=[
      'pandoc',str(gist.path),
      '-f', gist.ops['render']['from'],
      '-t', gist.ops['render']['to'],
      '-d', gist.ops['render']['defaults'],
      '-o', gist.ops['render']['output'],
      f'--resource-path={gist.path.parent}'],
      do_not_execute=dry_run)
    




#!/usr/bin/env python3
"""
Functions to convert gists using Pandoc
"""
import shutil
from pathlib import Path
from typing import Any, List, Callable
from functools import wraps
from jsonschema import validate

import gists
import shell


def __git_ignore_output(
  shrun: Callable[[List[str]], str], 
  gist: gists.Gist,
  dry_run: bool): 

    output_path: Path = Path(gist.ops['render']['output'])
    try:
        # https://git-scm.com/docs/git-check-ignore
        shrun(cmd=['git','check-ignore','--quiet',str(output_path)])
        return # already ignored
    except shell.ShellError:
        pass

    if dry_run:
        return # Do nothing, please ...

    # Ignore output file locally
    gitignore_path: Path = gist.path.parent.joinpath('.gitignore')
    with open(gitignore_path, 'a+', encoding='UTF-8') as gitignore_file:
        gitignore_file.write(f'\n{output_path.name}')



def __parametrized(func):
    @wraps(func)
    def decorator_func(*args, **kwargs) -> Any:

        gist: gists.Gist = \
             args[1] if len(args) > 0 else kwargs['gist']
        if 'publish' not in gist.ops:
            return None # ok, not all gists are published

        # Validate pandoc parameters
        validate(instance=gist.ops['publish'], schema={
          "type": "array",
          "items": {
            "type" : "object",
            "description": "Publish Operation",
            "properties": {
              "tmpl":{"type":"string","description":"Path to pandoc defaults file"},
              "exe":{"type":"string","description":"Path to executable for publishing"}
            },
            "required":["exe"]
          }
        })
        
        if not Path(gist.ops['publish']['tmpl']).exists():
            raise gists.GistError(f"{gist.ops['publish']['tmpl']} does not exist")

        if not Path(gist.ops['publish']['exe']).exists():
            raise gists.GistError(f"{gist.ops['publish']['exe']} does not exist")

        # Ensure output path
        tmp_path = gist.path.parent.join('.gistops')
        try:
            if tmp_path.exists():
                shutil.rmtree(str(tmp_path))
            tmp_path.mkdir()
            
            return func(*args, **kwargs)

        finally:
            if tmp_path.exists():
                shutil.rmtree(str(tmp_path))

    return decorator_func


@__parametrized
def publish(
  shrun: Callable[[List[str]], str], 
  gist: gists.Gist, 
  dry_run: bool = False):
    """Converts gists using pandoc and configuration from .gitattributes""" 

    if 'git-ignore' in gist.ops['render'] and gist.ops['render']['git-ignore']:
        __git_ignore_output(shrun=shrun, gist=gist, dry_run=dry_run)
     
    tmp_path = gist.path.parent.join('.gistops')
    
    # Todo: 
    # render pandoc.j2
    # parse output format

    shrun(cmd=[
      'pandoc',str(gist.path),
      '-d', gist.ops['render']['defaults'],
      '-o', str(output_path),
      f'--resource-path={gist.path.parent}'],
      do_not_execute=dry_run)

    shrun(cmd=[ 
      f'"{str(gist.root.joinpath(gist.ops["publish"]["callback"]))}"', 
      f'"{str(gist.path)}"', 
      json.dumps(json.dumps(gist.ops,separators=(',', ':'))) ], 
      do_not_execute=dry_run)

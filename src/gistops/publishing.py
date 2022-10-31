#!/usr/bin/env python3
"""
Functions to convert gists using Pandoc
"""
import shutil
import json
from pathlib import Path
from typing import Any, List, Callable
from functools import wraps
from jsonschema import validate
from dataclasses import asdict

import yaml
from jinja2 import Environment, BaseLoader

import gists
import shell


##################
# EXPORTED TYPES #
##################
class PublishError(Exception):
    """ GistOps publishing error """


#####################
# PRIVATE FUNCTIONS #
#####################
def __output_dir(gops: gists.GistOps) -> Path:
    return gops.path.parent.joinpath('.gistops')


def __pandoc_j2_path(gops: gists.GistOps, callback_path: Path) -> Path:
    for tmpl_path in [
      gops.path.parent.joinpath(f'{callback_path.stem}.pandoc.yml'),
      gops.path.parent.joinpath(f'{callback_path.stem}.pandoc.yaml'),
      callback_path.parent.joinpath(f'{callback_path.stem}.pandoc.yml'),
      callback_path.parent.joinpath(f'{callback_path.stem}.pandoc.yaml') ]:
        if tmpl_path.exists():
            return tmpl_path
    
    raise PublishError(
      'Cannot find pandoc defaults template ' 
      f'for publishing {gops.path} with {callback_path}')


def __ensure_output_dir(
  shrun: Callable[[List[str]], str], 
  gops: gists.GistOps,
  dry_run: bool): 

    output_dir: Path = __output_dir(gops)
    try:
        # https://git-scm.com/docs/git-check-ignore
        shrun(cmd=['git','check-ignore','--quiet',f'{str(output_dir)}/'])
    except shell.ShellError:
        if dry_run:
            return # Do nothing, please ...
        
        # Ignore output file locally
        gitignore_path: Path = gops.path.parent.joinpath('.gitignore')
        with open(gitignore_path, 'a+', encoding='UTF-8') as gitignore_file:
            gitignore_file.write(f'\n{output_dir.name}/')

    # Ensure path exists and is clean
    if output_dir.exists():
        shutil.rmtree(str(output_dir))
    output_dir.mkdir() # no parents, please parents should exist, otherwise crash


def __clean_output_dir(gops: gists.GistOps, dry_run: bool):
    if dry_run:
        return

    output_dir: Path = __output_dir(gops)
    if output_dir.exists():
        shutil.rmtree(str(output_dir))


def __parametrized(func):
    @wraps(func)
    def decorator_func(*args, **kwargs) -> Any:

        shrun: Callable[[List[str]], str] = \
             args[0] if len(args) >= 1 else kwargs['shrun']
        gops: gists.GistOps = \
             args[1] if len(args) > 0 else kwargs['gops']
        dry_run: bool = \
             args[2] if len(args) > 1 else kwargs['dry_run']
        if 'publish' not in gops.ops:
            return None # ok, not all gists are published

        # Validate pandoc parameters
        validate(instance=gops.ops['publish'], schema={
          "type": "array",
          "items": {
            "type" : "object",
            "description": "Publish Operation",
            "properties": {
              "exe": {"type": "string", "description": "Path to executable for publishing"},
              "args": {"type": "array", "items": {"type":"string"} }
            },
            "required":["exe"]
          }
        })

        for pbl in gops.ops['publish']:
            callback_path = Path(pbl['exe'])
            if not callback_path.exists():
                raise PublishError(
                  f"Publish Callback {callback_path} does not exist")

            __pandoc_j2_path(gops, callback_path)

        try:
            __ensure_output_dir(shrun=shrun, gops=gops, dry_run=dry_run)
            
            return func(*args, **kwargs)

        finally:
            __clean_output_dir(gops=gops, dry_run=dry_run)

    return decorator_func


######################
# EXPORTED FUNCTIONS #
######################
@__parametrized
def publish(
  shrun: Callable[[List[str]], str], 
  gops: gists.GistOps, 
  dry_run: bool = False):
    """Publish gists using pandoc configuration and publishing executable(s)""" 

    output_dir = __output_dir(gops)

    for pbl in gops.ops['publish']:
        callback_path = Path(pbl['exe'])

        # Render pandoc config
        pandoc_j2_path = __pandoc_j2_path(gops, callback_path)
        with open(pandoc_j2_path, 'r', encoding='utf-8') as pandoc_j2_file:
            pandoc_j2_tmpl = Environment(loader=BaseLoader()).from_string(
              pandoc_j2_file.read())
            pandoc_cfg_str: str = pandoc_j2_tmpl.render( gists.j2_params(gops) )

        try:
            pandoc_cfg: dict = yaml.safe_load(pandoc_cfg_str)
        except yaml.YAMLError as err:
            raise PublishError(
              f'Pandoc configuration {pandoc_j2_path} is invalid') from err

        pandoc_cfg_outpath = output_dir.joinpath(f'{pandoc_j2_path.name}.rendered')
        with open(pandoc_cfg_outpath,'w',encoding='utf-8') as pandoc_cfg_outfile:
            pandoc_cfg_outfile.write( yaml.dump(pandoc_cfg) )

        # Extract output file extension
        if 'to' not in pandoc_cfg:
            raise PublishError(
              f'Required "to" option not found in configuration {pandoc_j2_path}'
              'See --to option in https://pandoc.org/MANUAL.html')

        output_filepath = output_dir.joinpath(
          f'{gops.path.stem}.{pandoc_cfg["to"]}')

        # Render with Pandoc
        shrun(
          cmd=[
            'pandoc',str(gops.path),
            '-d', str(pandoc_cfg_outpath), 
            '-o', str(output_filepath),
            f'--resource-path={gops.path.parent}'],
          do_not_execute=dry_run)

        # Publish with Callback
        cmd=[
          f'"{str(callback_path.resolve())}"', 
          str(output_filepath),
          json.dumps(json.dumps(gists.j2_params(gops),separators=(',', ':'))) ]
        if 'args' in pbl:
            cmd.extend(pbl['args'])

        shrun(cmd, do_not_execute=dry_run)

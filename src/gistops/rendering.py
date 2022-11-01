#!/usr/bin/env python3
"""
Functions to render gists using Pandoc
"""
import shutil
from pathlib import Path
from typing import Any, List, Callable
from functools import wraps

import yaml
from jinja2 import Environment, BaseLoader

import gists
import shell


#####################
# PRIVATE FUNCTIONS #
#####################
def __tmp_dir(gist: gists.Gist) -> Path:
    return gist.path.parent.joinpath(gists.gitignored_path())


def __ensure_tmp_dir(
  shrun: Callable[[List[str]], str], 
  gist: gists.Gist): 

    tmp_dir: Path = __tmp_dir(gist)
    gists.ensure_gitignore(
      shrun, 
      gist.path.parent, 
      f'{str(tmp_dir.relative_to(gist.path.parent))}/')

    # Ensure path exists and is clean
    if tmp_dir.exists():
        shutil.rmtree(str(tmp_dir))
    tmp_dir.mkdir() # no parents, please parents should exist, otherwise crash


def __clean_tmp_dir(gist: gists.Gist):
    tmp_dir: Path = __tmp_dir(gist)
    if tmp_dir.exists():
        shutil.rmtree(str(tmp_dir))


def __resolve_j2(pandoc_j2_path: Path, gist:gists.Gist) -> Path:
    tmp_dir = __tmp_dir(gist)

    # Render pandoc config
    with open(pandoc_j2_path, 'r', encoding='utf-8') as pandoc_j2_file:
        pandoc_j2_tmpl = Environment(loader=BaseLoader()).from_string(
          pandoc_j2_file.read())
        pandoc_yml_str: str = pandoc_j2_tmpl.render( gists.j2_params(gist) )

    try:
        pandoc_yml: dict = yaml.safe_load(pandoc_yml_str)
    except yaml.YAMLError as err:
        raise gists.GistOpsError(
          f'Pandoc configuration {pandoc_j2_path} is invalid') from err

    # Extract output file extension
    if 'to' not in pandoc_yml:
        raise gists.GistOpsError(
          f'Required "to" option not found in configuration {pandoc_j2_path}'
          'See --to option in https://pandoc.org/MANUAL.html')

    pandoc_yml_path = tmp_dir.joinpath(f'{pandoc_yml["to"]}.{pandoc_j2_path.name}')
    with open(pandoc_yml_path,'w',encoding='utf-8') as pandoc_yml_file:
        pandoc_yml_file.write( yaml.dump(pandoc_yml) )

    return pandoc_yml_path


def __templated(func):
    @wraps(func)
    def decorator_func(*args, **kwargs) -> Any:

        shrun: Callable[[List[str]], str] = \
             args[0] if len(args) >= 1 else kwargs['shrun']
        gist: gists.Gist = \
             args[1] if len(args) > 0 else kwargs['gist']

        try:
            __ensure_tmp_dir(shrun=shrun, gist=gist)
            
            return func(*args, **kwargs)

        finally:
            __clean_tmp_dir(gist=gist)

    return decorator_func


######################
# EXPORTED FUNCTIONS #
######################
@__templated
def render(
  shrun: Callable[[List[str]], str], 
  gist: gists.Gist, 
  dry_run: bool = False) -> List[Path]:
    """Render gists using pandoc configurations""" 

    rendered = []
    for pandoc_j2_path in gist.path.parent.glob('*.pandoc.j2.yml'):

        # Render pandoc config
        pandoc_yml_path = __resolve_j2(pandoc_j2_path, gist)
        out_format = pandoc_yml_path.name.split('.')[0]

        # Render with Pandoc
        output_filepath = gist.path.parent.joinpath(
          f'{pandoc_j2_path.name}.{out_format}') 

        if not output_filepath.exists():
            gists.ensure_gitignore(
              shrun, gist.path.parent, str(output_filepath.name))
        else:
            output_filepath.unlink()

        shrun(
          cmd=[
            'pandoc',str(gist.path),
            '-d', str(pandoc_yml_path), 
            '-o', str(output_filepath),
            f'--resource-path={gist.path.parent}'],
          do_not_execute=dry_run)

        rendered.append(output_filepath)
    return rendered


@__templated
def cleanup(
  gist: gists.Gist, 
  dry_run: bool = False):
    """Cleanup rendered gists""" 

    for pandoc_j2_path in gist.path.parent.glob('*.pandoc.j2'):
        # Render pandoc config
        pandoc_yml_path = __resolve_j2(pandoc_j2_path, gist)
        out_format = pandoc_yml_path.name.split('.')[0]

        # Render with Pandoc
        output_filepath = gist.path.parent.joinpath(
          f'{pandoc_j2_path.name}.{out_format}') 

        if dry_run:
            continue

        if output_filepath.exists() and output_filepath.is_file():
            output_filepath.unlink()

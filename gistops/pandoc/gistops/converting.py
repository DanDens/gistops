#!/usr/bin/env python3
"""
Functions to render gists using Pandoc
"""
import logging
from pathlib import Path
from functools import wraps
from typing import Callable, List, Any

import yaml
from jinja2 import BaseLoader, Environment

import shell
import gists


def __render_j2(gist:gists.Gist, pandoc_j2_path: Path) -> dict:
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

    return pandoc_yml


def __ensure_gitignore(
  shrun: Callable[[List[str]], str], 
  gitignore_parent: Path,
  ignore_pattern: str ):
    """Ensure gitignore added for pattern"""
    try:
        # https://git-scm.com/docs/git-check-ignore
        shrun(cmd=['git','check-ignore','--quiet', 
          f'{str(gitignore_parent)}/{ignore_pattern}' ])
    except shell.ShellError:
        # Ignore output file locally
        gitignore_path: Path = gitignore_parent.joinpath('.gitignore')
        with open(gitignore_path, 'a+', encoding='UTF-8') as gitignore_file:
            gitignore_file.write(f'\n{ignore_pattern}')


def __gitignore_new(func):
    """Can be used to ensure new files or directories are ignored"""
    @wraps(func)
    def decorator_func(*args, **kwargs) -> Any:

        shrun: Callable[[List[str]], str] = \
             args[0] if len(args) >= 1 else kwargs['shrun']
        gist: gists.Gist = \
             args[1] if len(args) > 0 else kwargs['gist']

        pre_existing = list(gist.path.parent.iterdir())
        
        try:
            return func(*args, **kwargs)
        finally:
            for ignore_candidate in gist.path.parent.iterdir():
                if ignore_candidate in pre_existing:
                    continue

                if ignore_candidate.is_file():
                    ignore_pattern = ignore_candidate.name
                elif ignore_candidate.is_dir():
                    ignore_pattern = f'{ignore_candidate.name}/'
                
                __ensure_gitignore(
                  shrun, gist.path.parent, ignore_pattern)

    return decorator_func


######################
# EXPORTED FUNCTIONS #
######################
@__gitignore_new
def convert(
  shrun: Callable[[List[str]], str], 
  gist: gists.Gist,
  outpath: Path,
  dry_run: bool = False) -> List[gists.ConvertedGist]:
    """Convert gists using pandoc configurations""" 
    logger = logging.getLogger()

    convs: List[gists.ConvertedGist] = []
    for pandoc_j2_path in sorted(
      list(gist.path.parent.glob('*.pandoc.j2')), 
      key=str):

        # Render pandoc config
        pandoc_yml = __render_j2(gist, pandoc_j2_path)

        # Write pandoc defaults to disk
        pandoc_yml_path = outpath.joinpath(pandoc_j2_path.parent).joinpath(
          f'{pandoc_j2_path.stem}.yml')

        logger.info(f'> echo "..." > {pandoc_yml_path} ')
        if not dry_run:
            pandoc_yml_path.parent.mkdir(parents=True, exist_ok=True)
            with open(pandoc_yml_path,'w',encoding='utf-8') as pandoc_yml_file:
                pandoc_yml_file.write( yaml.dump(pandoc_yml) )

        # Convert using Pandoc Configuration
        output_filepath = outpath.joinpath(pandoc_j2_path.parent).joinpath(
          f'{gist.path.stem}.{pandoc_yml["to"]}') 

        if output_filepath.exists():
            logger.info(f'> rm {output_filepath} ')
            if not dry_run:
                output_filepath.unlink()

        if not dry_run:
            output_filepath.parent.mkdir(parents=True, exist_ok=True)
        shrun(
          cmd=[
            'pandoc',str(gist.path),
            '-d', f'"{str(pandoc_yml_path)}"', 
            '-o', f'"{str(output_filepath)}"',
            f'--resource-path={gist.path.parent}'],
          do_not_execute=dry_run)

        if 'metadata' in pandoc_yml and 'title' in pandoc_yml['metadata']:
            title = pandoc_yml['metadata']['title']
        else:
            title = f'{gist.path.parent.name}-{gist.path.name}'

        convs.append(gists.ConvertedGist(
          gist=gist,
          title=title,
          path=output_filepath,
          deps=[gist.path.parent.joinpath(r) for r in pandoc_yml['resource-path']] ))
    return convs


def cleanup(
  gist: gists.Gist, 
  outpath: Path,
  dry_run: bool = False):
    """Cleanup converted gists""" 
    logger = logging.getLogger()

    for pandoc_j2_path in gist.path.parent.glob('*.pandoc.j2'):

        # Render pandoc config
        pandoc_yml = __render_j2(gist, pandoc_j2_path)

        # Delete converted files
        pandoc_yml_path = outpath.joinpath(pandoc_j2_path.parent).joinpath(
          f'{pandoc_j2_path.stem}.yml')
        if pandoc_yml_path.exists() and pandoc_yml_path.is_file():
            logger.info(f'> rm {pandoc_yml_path} ')
            if not dry_run: 
                pandoc_yml_path.unlink()

        output_filepath = outpath.joinpath(pandoc_j2_path.parent).joinpath(
          f'{gist.path.stem}.{pandoc_yml["to"]}') 
        if output_filepath.exists() and output_filepath.is_file():
            logger.info(f'> rm {output_filepath} ')
            if not dry_run:
                output_filepath.unlink()

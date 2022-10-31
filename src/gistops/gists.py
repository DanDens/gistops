#!/usr/bin/env python3
"""
Gist Representation and Factories
"""
import os
import json
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import List, Callable, Iterator

from jsonschema import validate
from jinja2 import Environment, BaseLoader

import shell


class GistError(Exception):
    """ Gist representation error """


@dataclass
class Gist:
    """ Gist representation """
    root: Path
    path: Path
    ops: dict


def __load_gist(
    git_root: Path,
    gist_path: Path, 
    gistops_j2: str) -> Gist:

    gistops_j2_tmpl = Environment(loader=BaseLoader()).from_string(gistops_j2)
    gistops_str: str = gistops_j2_tmpl.render({
        'root': str(git_root),
        'dir': str(gist_path.parent),
        'file': str(gist_path.name),
        'stem': str(gist_path.stem),
        'suffix': str(gist_path.suffix)
    })

    gistops: dict = json.loads(gistops_str)
    validate(instance=gistops, schema={
        "type": "object",
        "properties": {
            "publish": {
                "type": "array",
                "description": "Publishing Operations",
                "items": {"type":"object"}
            }
        }
    })

    return Gist(git_root, gist_path, gistops)


def assert_git_root(gist_absolute_path: Path) -> Path:
    """Locate git root directory from gist_path"""
    if not gist_absolute_path.exists():
        raise RuntimeError(f'{gist_absolute_path} does not exist')

    #############
    # .git root # 
    #############
    def traverse_upwards(gist_path: Path) -> Path:
        if gist_path == gist_path.parent:
            return None

        if gist_path.is_dir():
            if len(list(gist_path.glob('.git'))) == 1:
                return gist_path

        return traverse_upwards(gist_path.parent)

    git_root_path = traverse_upwards(gist_absolute_path.resolve())
    if not git_root_path:
        raise GistError(
            f'{gist_absolute_path} is not in a git repository. '
            'Please run from valid git repository')

    return git_root_path


def __gistops_attribute() -> str:
    return '[attr]gistops'


def __assert_gistops_attribute(
  shrun: Callable[[List[str],bool], str],
  git_root: Path) -> Path:  
    """Verify [attr]gistops definition stored in .gitattributes"""

    # See DEFINING MACRO ATTRIBUTES in 
    # https://git-scm.com/docs/gitattributes
    # https://stackoverflow.com/questions/28026767/where-should-i-place-my-global-gitattributes-file
    attr_paths = [ 
      Path(git_root.joinpath('.git/info/attributes')), 
      Path(git_root.joinpath('.gitattributes')) ]

    try:
        global_attr_file = Path(
          shrun(
            cmd=['git','config','--global','--get','core.attributesfile'],
            enforce_absolute_silence=True) )
        attr_paths += global_attr_file
    except shell.ShellError as _:
        pass

    if 'HOME' in os.environ:
        attr_paths.append(
          Path(os.environ.get('HOME')).joinpath('.config/git/attributes'))

    for candidate_path in attr_paths:
        if not candidate_path.exists() or not candidate_path.is_file():
            continue

        try:
            attr_path = candidate_path.relative_to(git_root)
        except ValueError:
            attr_path = candidate_path

        # Try to open as location
        try:
            with open(str(attr_path),'r',encoding='utf-8') as candidate_file:
                candidate_attrs = candidate_file.read()
                if candidate_attrs.find(__gistops_attribute()) >= 0:
                    return attr_path
        except IOError:
            pass

    raise GistError(
        'Could not locate [attr]gistops in any known '
        '.gitattribute or gitattributes file. '
        'Please run "gistops init" first')


def init_gistops(
  shrun: Callable[[List[str],bool], str],
  git_root: Path):
    """Configure git repository to use gistops"""
    logger = logging.getLogger()

    # Ensure gistops attribute
    try:
        __assert_gistops_attribute(shrun, git_root)
    except GistError:
        # Create '.git/info/attributes' file
        logger.info(f'Adding {__gistops_attribute()} to .git/info/attributes')
        with open(git_root.joinpath('.git/info/attributes'),
          'a+', encoding='utf-8') as git_attributes_file:
            git_attributes_file.write(f'\n{__gistops_attribute()}')

    # TODO: .gitignore -> .gistops/


def iterate_gists(
  shrun: Callable[[List[str],bool], str], 
  git_root: Path,
  gist_path: Path,
  git_diff_hash: str) -> Iterator[Gist]:
    """Locate gists in path using gistops attribute stored in .gitattributes"""
    logger = logging.getLogger()

    __assert_gistops_attribute(shrun=shrun, git_root=git_root)

    gist_absolute_path = git_root.joinpath(gist_path).resolve()

    git_diff_files: List[Path] = None
    if git_diff_hash is not None:
        # https://git-scm.com/docs/git-diff-tree
        git_diff_files = [Path(fc) for fc in shrun(
            cmd=['git','diff-tree','--no-commit-id','--name-only','-r', git_diff_hash]
          ).splitlines()]

    if gist_absolute_path.is_dir():
        for git_abspath in gist_absolute_path.glob('**/'):
            if not git_abspath.is_dir():
                continue # not a directory

            try:
                if git_abspath.relative_to(git_root.joinpath('.git')):
                    continue # ignore .git sub directory
            except ValueError:
                pass

            git_dir = git_abspath.relative_to(git_root)

            # https://git-scm.com/docs/git-check-attr and 
            # https://git-scm.com/docs/git-ls-files
            # Files with gistops .gitattribute listed as 
            # README.md: gistops: {"render":{...}}
            for gitattr in shrun(
              cmd=[
                'git','ls-files','|','git','check-attr',
                'gistops',f'{str(git_dir)}/*.*'],
              log_cmd_level=logging.DEBUG, hide_streams=True).splitlines():

                if gitattr.split(': ')[-1] == 'unspecified':
                    continue # no gistops flag on this one

                gist_file, _, gistops_j2 = gitattr.split(': ')
                if git_diff_files is not None and \
                    Path(gist_file) not in git_diff_files:
                    logger.info(f'{gist_file} unchanged for {git_diff_hash}')
                    continue

                yield __load_gist(
                    git_root=git_root,
                    gist_path=Path(gist_file),
                    gistops_j2=gistops_j2 )

    elif gist_absolute_path.is_file():
        # https://git-scm.com/docs/git-check-attr
        gitattr = shrun(cmd=['git','check-attr','gistops', str(gist_path)])
        if gitattr != '': 
            gist_file, _, gistops_j2 = gitattr.split(' ')
            if git_diff_files is None or \
                Path(gist_file) in git_diff_files:    

                yield __load_gist(
                  git_root=git_root,
                  gist_path=gist_absolute_path.relative_to(
                    git_root).joinpath(gist_file),
                  gistops_j2=gistops_j2 )

    else:
        raise GistError(
            f'{gist_path} is symbolic link. '
            'Symbolic links are not supported.'
            'Please provide file or directory')

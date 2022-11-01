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

import shell

##################
# EXPORTED TYPES #
##################
class GistOpsError(Exception):
    """ GistOps representation error """


@dataclass
class Gist:
    """ Gist representation """
    root: Path
    path: Path
    tags: dict
    commit_id: str


def j2_params(gist: Gist) -> dict:
    """Returns the gist as dict"""
    return {
      'root': str(gist.root),
      'path': str(gist.path),
      'name': str(gist.path.name),
      'dir': str(gist.path.parent),
      'stem': str(gist.path.stem),
      'suffix': str(gist.path.suffix),
      'parent': str(gist.path.parent.name),
      'tags': gist.tags,
      'commit_id': str(gist.commit_id)
    }

#####################
# PRIVATE FUNCTIONS #
#####################
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

    raise GistOpsError(
        'Could not locate [attr]gistops in any known '
        '.gitattribute or gitattributes file. '
        'Please run "gistops init" first')


######################
# EXPORTED FUNCTIONS #
######################
def gitignored_path() -> Path:
    """Path used for hiding temporary files"""
    return Path('.gistops')


def ensure_gitignore(
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


def assert_git_root(gist_absolute_path: Path) -> Path:
    """Locate git root directory from gist_path"""
    if not gist_absolute_path.exists():
        raise GistOpsError(f'{gist_absolute_path} does not exist')

    def traverse_upwards(gist_path: Path) -> Path:
        if gist_path == gist_path.parent:
            return None

        if gist_path.is_dir():
            if len(list(gist_path.glob('.git'))) == 1:
                return gist_path

        return traverse_upwards(gist_path.parent)

    git_root_path = traverse_upwards(gist_absolute_path.resolve())
    if not git_root_path:
        raise GistOpsError(
            f'{gist_absolute_path} is not in a git repository. '
            'Please run from valid git repository')

    return git_root_path


def init_gistops(
  shrun: Callable[[List[str],bool], str],
  git_root: Path):
    """Configure git repository to use gistops"""
    logger = logging.getLogger()

    # Ensure gistops attribute
    try:
        __assert_gistops_attribute(shrun, git_root)
    except GistOpsError:
        # Create '.git/info/attributes' file
        logger.info(f'Adding {__gistops_attribute()} to .git/info/attributes')
        with open(git_root.joinpath('.git/info/attributes'),
          'a+', encoding='utf-8') as git_attributes_file:
            git_attributes_file.write(f'\n{__gistops_attribute()}')

    # Ensure gitignored path is actually ignored
    ensure_gitignore(shrun, git_root, gitignored_path())


def iterate_gists(
  shrun: Callable[[List[str],bool], str], 
  git_root: Path,
  gist_path: Path,
  git_diff_hash: str) -> Iterator[Gist]:
    """Locate gists in path using gistops attribute stored in .gitattributes"""
    logger = logging.getLogger()

    __assert_gistops_attribute(shrun=shrun, git_root=git_root)

    gist_absolute_path = git_root.joinpath(gist_path).resolve()
    git_commit_id = shrun(
      cmd=['git', 'log', '-1', '--pretty=%h'],
      log_cmd_level=logging.DEBUG, 
      hide_streams=True).strip()

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

                gist_file, _, gist_tags = gitattr.split(': ')
                if git_diff_files is not None and \
                    Path(gist_file) not in git_diff_files:
                    logger.info(f'{gist_file} unchanged for {git_diff_hash}')
                    continue

                yield Gist(
                  git_root, 
                  Path(gist_file), 
                  json.loads(gist_tags) if gist_tags != 'set' else {}, 
                  git_commit_id)

    elif gist_absolute_path.is_file():
        # https://git-scm.com/docs/git-check-attr
        gitattr = shrun(cmd=['git','check-attr','gistops', str(gist_path)])
        if gitattr != '': 
            gist_file, _, gist_tags = gitattr.split(' ')
            if git_diff_files is None or \
                Path(gist_file) in git_diff_files:

                yield Gist(
                  git_root, 
                  gist_absolute_path.relative_to(
                    git_root).joinpath(gist_file), 
                  json.loads(gist_tags) if gist_tags != 'set' else {}, 
                  git_commit_id)

    else:
        raise GistOpsError(
            f'{gist_path} is symbolic link. '
            'Symbolic links are not supported.'
            'Please provide file or directory')

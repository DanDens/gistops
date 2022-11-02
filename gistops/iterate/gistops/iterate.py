#!/usr/bin/env python3
"""
Gist Representation and Factories
"""
import os
import json
import logging
from pathlib import Path
from typing import List, Callable, Iterator

import shell
import gists


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

    raise gists.GistOpsError(
        'Could not locate [attr]gistops in any known '
        '.gitattribute or gitattributes file. '
        'Please run "gistops init" first')


######################
# EXPORTED FUNCTIONS #
######################
def init_gistops(
  shrun: Callable[[List[str],bool], str],
  git_root: Path):
    """Configure git repository to use gistops"""
    logger = logging.getLogger()

    # Ensure gistops attribute
    try:
        __assert_gistops_attribute(shrun, git_root)
    except gists.GistOpsError:
        # Create '.git/info/attributes' file
        logger.info(f'Adding {__gistops_attribute()} to .git/info/attributes')
        with open(git_root.joinpath('.git/info/attributes'),
          'a+', encoding='utf-8') as git_attributes_file:
            git_attributes_file.write(f'\n{__gistops_attribute()}')


def iterate_gists(
  shrun: Callable[[List[str],bool], str], 
  git_root: Path,
  gist_path: Path,
  git_diff_hash: str) -> Iterator[gists.Gist]:
    """Locate gists in path using gistops attribute stored in .gitattributes"""
    logger = logging.getLogger()

    __assert_gistops_attribute(shrun=shrun, git_root=git_root)

    gist_absolute_path = git_root.joinpath(gist_path).resolve()
    git_commit_id = shrun(
      cmd=['git', 'log', '-1', '--pretty=%h']).strip()

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
                'gistops',f'{str(git_dir)}/*.*']).splitlines():

                if gitattr.split(': ')[-1] == 'unspecified':
                    continue # no gistops flag on this one

                gist_file, _, gist_tags = gitattr.split(': ')
                if git_diff_files is not None and \
                    Path(gist_file) not in git_diff_files:
                    logger.info(f'{gist_file} unchanged for {git_diff_hash}')
                    continue

                yield gists.Gist(
                  path=Path(gist_file), 
                  commit_id=git_commit_id,
                  tags=json.loads(gist_tags) if gist_tags != 'set' else {} )

    elif gist_absolute_path.is_file():
        # https://git-scm.com/docs/git-check-attr
        gitattr = shrun(cmd=['git','check-attr','gistops', str(gist_path)])
        if gitattr != '': 
            gist_file, _, gist_tags = gitattr.split(' ')
            if git_diff_files is None or \
                Path(gist_file) in git_diff_files:

                yield gists.Gist(
                  path=gist_absolute_path.relative_to(
                    git_root).joinpath(gist_file), 
                  commit_id=git_commit_id,
                  tags=json.loads(gist_tags) if gist_tags != 'set' else {})

    else:
        raise gists.GistOpsError(
            f'{gist_path} is symbolic link. '
            'Symbolic links are not supported.'
            'Please provide file or directory')

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


def __init_gistops(
  git_root: Path):
    """Configure git repository to use gistops"""
    logger = logging.getLogger()

    # File directory
    attributes_dir = git_root.joinpath('.git').joinpath('info')
    attributes_dir.mkdir(parents=True,exist_ok=True)

    # Create '.git/info/attributes' file
    logger.info(f'Adding {__gistops_attribute()} to {attributes_dir.joinpath("attributes")}')
    with open(attributes_dir.joinpath("attributes"), 'a+', encoding='utf-8') as git_attributes_file:
        git_attributes_file.write(f'\n{__gistops_attribute()}')


def __ensure_gistops_attribute(
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

    __init_gistops(git_root=git_root)


######################
# EXPORTED FUNCTIONS #
######################
def iterate_gists(
  shrun: Callable[[List[str],bool], str], 
  git_root: Path,
  gist_path: Path,
  git_diff_hash: str) -> Iterator[gists.Gist]:
    """Locate gists in path using gistops attribute stored in .gitattributes"""
    logger = logging.getLogger()

    __ensure_gistops_attribute(shrun=shrun, git_root=git_root)

    gist_absolute_path = git_root.joinpath(gist_path).resolve()
    git_commit_id = shrun(
      cmd=['git', 'log', '-1', '--pretty=%h']).strip()

    git_diff_files: List[Path] = None
    if git_diff_hash is not None:
        # https://git-scm.com/docs/git-diff-tree
        git_diff_files = [Path(fc) for fc in shrun(
            cmd=['git','diff-tree','--no-commit-id','--name-only','-r', git_diff_hash]
          ).splitlines()]

    if not gist_absolute_path.is_dir():
        raise gists.GistOpsError(
            f'{gist_path} is file or symbolic link. '
            'Symbolic links are not supported.'
            'Please provide directory as input')

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
        for git_ls_file in shrun(
          cmd=['git','ls-files','--directory',f'"{str(git_dir)}"']).splitlines():

            if Path(git_ls_file).parent != git_dir:
                continue # ... only files of this directory please

            gitattr = shrun(
              cmd=['git', 'check-attr', 'gistops', '--', f'"{git_ls_file}"']).rstrip('\r\n')

            if gitattr.split(': ')[-1].find('unspecified') >= 0:
                continue # no gistops flag on this one

            gist_file, _, gist_tags = gitattr.split(': ')
            gist_file_path = Path(gist_file)
            if git_diff_files is not None and \
                gist_file_path not in git_diff_files:
                logger.info(f'{gist_file} unchanged for {git_diff_hash}')
                continue

            yield gists.Gist(
              path=gist_file_path, 
              commit_id=git_commit_id,
              tags=json.loads(gist_tags) if gist_tags != 'set' else {},
              resources=[f'{str(gist_file_path.parent)}:**/*.*'],
              trace_id=str(gist_file_path),
              title=f'{gist_file_path.parent.name}-{gist_file_path.name}' )

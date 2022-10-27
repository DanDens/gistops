#!/usr/bin/env python3
"""
Functions to mirror branches for git remotes
"""
import re
import logging
from dataclasses import dataclass
from typing import Any, List, Callable
from urllib.parse import urlparse, ParseResult
from functools import wraps

@dataclass
class GitRemote:
    """Represents a Git Remote Repository"""
    url: str
    name: str


def as_remote(
  shrun: Callable[[List[str]], str],
  url: str,
  username: str,
  password: str) -> GitRemote:
    """Builds git remote from given parammeters"""
    parts: ParseResult = urlparse(url)

    # Allowed characters in remote references are
    # https://mirrors.edge.kernel.org/pub/software/scm/git/docs/git-check-ref-format.html
    subs = '|'.join(
      [re.escape(sub) for sub in ['~','..','^','/','//',' ?','*','[',']','@{','@'] ])
    remote_name = re.sub(f'({subs})','.', f'{parts.netloc}{parts.path}')
    shrun(cmd=['git','check-ref-format','--branch',remote_name])

    oauth2 = ''
    if username is not None and password is not None:
        oauth2 = f'{username}:{password}@'

    return GitRemote(
        url=f'{parts.scheme}://{oauth2}{parts.netloc}{parts.path}',
        name=remote_name )


def __exists_remote(
    shrun: Callable[[List[str]], str], git_remote: GitRemote) -> bool:

    return git_remote.name.strip() in [
      rm.strip() for rm in shrun(cmd=['git', 'remote']).splitlines() ]


def __reset_remote(
    shrun: Callable[[List[str]], str], git_remote: GitRemote):

    if __exists_remote(shrun, git_remote):
        __remove_remote(shrun, git_remote)

    shrun(
        cmd=['git', 'remote', 'add', git_remote.name, git_remote.url], 
        enforce_absolute_silence=True )


def __remove_remote(
    shrun: Callable[[List[str]], str], git_remote: GitRemote):

    if __exists_remote(shrun, git_remote):
        shrun(cmd=['git', 'remote', 'remove', git_remote.name])


def __ensure_remotes(func):
    @wraps(func)
    def decorator_func(*args, **kwargs) -> Any:
        shrun: Callable[[List[str]], str] = \
            args[0] if len(args)>0 else kwargs['shrun']
        git_remote_src: GitRemote = \
            args[1] if len(args) > 0 else kwargs['git_remote_src']
        git_remote_trg: GitRemote = \
            args[2] if len(args) > 1 else kwargs['git_remote_trg']
        try:
            __reset_remote(shrun, git_remote_src)
            __reset_remote(shrun, git_remote_trg)

            res = func(*args, **kwargs)
        except Exception as err:
            raise err
        finally:
            __remove_remote(shrun, git_remote_src)
            __remove_remote(shrun, git_remote_trg)

        return res

    return decorator_func


@__ensure_remotes
def mirror(
    shrun: Callable[[List[str]], str],
    git_remote_src: GitRemote,
    git_remote_trg: GitRemote,
    branch_regex: str,
    dry_run: bool = False):
    """Force mirror branches matching the given regex"""
    logger = logging.getLogger()

    git_res = shrun(cmd=['git','ls-remote','--heads', git_remote_src.name])

    branches: List[str] = list(re.findall(
        f'refs/heads/({branch_regex})$', git_res, re.MULTILINE))

    if len(branches) == 0:
        logger.info(f'No branches with "{branch_regex}" exist. Skipping ...')
        return

    # Fetch remote branches
    shrun(cmd=['git','fetch','-p',git_remote_src.name])
    shrun(cmd=['git','fetch','-p',git_remote_trg.name])

    # Push force branches to remote
    for branch in branches:
        shrun(
          cmd=[
            'git','push','-q','--force', f'{git_remote_trg.name}',
            f'refs/remotes/{git_remote_src.name}/{branch}:refs/heads/{branch}'],
          do_not_execute=dry_run)

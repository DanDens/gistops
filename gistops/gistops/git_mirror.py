#!/usr/bin/env python3
import re
import string
from dataclasses import dataclass
from typing import Any, List, Callable, NamedTuple
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit, ParseResult
from random import choice as random_choice
from functools import wraps


@dataclass
class GitRemote:
    """Represents a Git Remote Repository"""
    url: str
    name: str


def to_remote(url: str, username: str, password:str) -> GitRemote:
    """Builds git remote from given parammeters"""
    parts: ParseResult = urlsplit(url)
    
    unique = ''.join(
        [random_choice(string.ascii_lowercase) for _ in range(5)])
    unique += datetime.utcnow().strftime('-%Y%m%dt%H%M%S')
    
    return GitRemote(
        url=f'{parts.scheme}://{username}:{password}@{parts.netloc}{parts.path}',
        name=unique)


def __exists_remote(
    shrun: Callable[[List[str],bool], str], git_remote: GitRemote) -> bool:

    return git_remote.name.strip() in [
      rm.strip() for rm in shrun( cmd=['git', 'remote']).splitlines() ]


def __reset_remote(
    shrun: Callable[[List[str],bool], str], git_remote: GitRemote):

    if __exists_remote(shrun, git_remote):
        __remove_remote(shrun, git_remote)

    shrun( cmd=['git', 'remote', 'add', git_remote.name, git_remote.url] )


def __remove_remote(
    shrun: Callable[[List[str],bool], str], git_remote: GitRemote):

    if __exists_remote(shrun, git_remote):
        shrun(cmd=['git', 'remote', 'remove', git_remote.name])


def __ensure_remotes(func):
    @wraps(func)
    def decorator_func(*args, **kwargs) -> Any:
        shrun: Callable[[List[str],bool], str] = \
            args[0] if len(args)>0 else kwargs['shrun']
        git_remote_source: GitRemote = \
            args[1] if len(args) > 0 else kwargs['git_remote_source']
        git_remote_target: GitRemote = \
            args[2] if len(args) > 1 else kwargs['git_remote_target']
        try:
            __reset_remote(shrun, git_remote_source)
            __reset_remote(shrun, git_remote_target)

            res = func(*args, **kwargs)
        except Exception as err:
            raise err
        finally:
            __remove_remote(shrun, git_remote_source)
            __remove_remote(shrun, git_remote_target)

        return res

    return decorator_func


@__ensure_remotes
def mirror_remote(
    shrun: Callable[[List[str],bool], str],
    git_remote_source: GitRemote,
    git_remote_target: GitRemote,
    branch_regex: str):
    """Force mirror branches matching the given regex"""

    git_res = shrun(cmd=[
        'git','ls-remote','--heads', git_remote_source.name])
        
    branches: List[str] = [match for match in re.findall(
        f'refs/heads/({branch_regex})$', git_res, re.MULTILINE)]
         
    if len(branches) == 0:
        return

    # Fetch remote branches
    shrun( cmd=['git','fetch', '-p', git_remote_source.name] )
    shrun( cmd=['git','fetch', '-p', git_remote_target.name] )

    # Push force branches to remote
    for branch in branches:
        shrun(cmd=[
          'git','push','-q','--force', f'{git_remote_target.name}',
          f'refs/remotes/{git_remote_source.name}/{branch}:refs/heads/{branch}'] )
        

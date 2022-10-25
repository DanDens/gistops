#!/usr/bin/env python3
import re
import string
from dataclasses import dataclass
from typing import Any, List, Callable, NamedTuple
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit
from random import choice as random_choice
from functools import wraps


@dataclass
class GitRemote:
    """Represents a Git Remote Repository"""
    url: str
    name: str


def compile_remote(url: str, username: str, password:str) -> GitRemote:
    """Builds git remote from given parammeters"""
    parts: NamedTuple = urlsplit(url)
    parts.username = username
    parts.password = password

    unique = ''.join(
        [random_choice(string.ascii_lowercase) for _ in range(5)])
    unique += datetime.utcnow().strftime('-%Y%m%dt%H%M%S')

    return GitRemote(
        url=urlunsplit(parts),
        name=unique)


def __exists_remote(
    shell: Callable[[List[str],bool], str],
    git_remote: GitRemote) -> bool:

    return git_remote.name.strip() in [
      rm.strip() for rm in shell(cmd=['git', 'remote']).splitlines()]


def __reset_remote(
    shell: Callable[[List[str],bool], str],
    git_remote: GitRemote):

    if __exists_remote(shell, git_remote):
        __remove_remote(shell, git_remote)

    shell(cmd=['git', 'remote', 'add',
        git_remote.name, urlunsplit(git_remote.url)],
        enforce_silent=True)


def __remove_remote(
    shell: Callable[[List[str],bool], str],
    git_remote: GitRemote):

    if __exists_remote(shell, git_remote):
        shell(cmd=['git', 'remote', 'remove', git_remote.name])


def __ensure_remotes(func):
    @wraps(func)
    def decorator_func(*args, **kwargs) -> Any:
        shell: Callable[[List[str],bool], str] = \
            args[0] if len(args)>0 else kwargs['shell']
        git_remote_source: GitRemote = \
            args[1] if len(args) > 0 else kwargs['git_remote_source']
        git_remote_target: GitRemote = \
            args[2] if len(args) > 1 else kwargs['git_remote_target']
        try:
            __reset_remote(shell, git_remote_source)
            __reset_remote(shell, git_remote_target)

            res = func(args, kwargs)
        except Exception as err:
            raise err
        finally:
            __remove_remote(shell, git_remote_source)
            __remove_remote(shell, git_remote_target)

        return res

    return decorator_func

@__ensure_remotes
def mirror(
    shell: Callable[[List[str],bool], str],
    git_remote_source: GitRemote,
    git_remote_target: GitRemote,
    branch_regex: str):
    """Force mirror branches matching the given regex"""

    git_res = shell(cmd=[
        'git','ls-remote','--heads', git_remote_source.name])
    branches = [match[1] for match in re.findall(
        f'refs/heads/({branch_regex})$', git_res, re.MULTILINE)]

    # Prune remote tracking references no longer exist
    shell(cmd=['git','fetch','--prune'])

    for branch in branches:
        # Fetch remote branch at depth 1
        shell(cmd=['git','fetch','-k', git_remote_source.name, branch])
        # Force checkout branch locally
        shell(cmd=['git','branch','-d', branch])
        shell(cmd=['git','checkout', '-b', branch,
            f'{git_remote_source.name}/{branch}'])
        # Force overwrite remote branch
        shell(cmd=['git','push',
            '--set-upstream', git_remote_target.name,
            f'HEAD:${branch}', '--force'])

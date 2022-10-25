#!/usr/bin/env python3
from pathlib import Path
from functools import partial

from shell import run


def __add_mirror(git_remote_url:str, silent: bool):
  run(cmd=['git', 'remote', 'add', 'gistops-mirror', git_remote_url], silent=silent)


def __remove_mirror(silent: bool):
  run(cmd=['git', 'remote', 'remove', 'gistops-mirror'], silent=silent)


def __ensure_parameters(func):
  def decorator_func(
    branch_regex: str, git_remote_url: str, git_root: Path, silent: bool):
    
    # Compute actual git root 
    # Todo ...

    # Check git remote url exists
    # Todo ...
      
    # getting the returned value
    res = func(branch_regex, git_remote_url, git_root, silent)

    # returning the value to the original frame
    return res
  return decorator_func


@__ensure_parameters
def push(branch_regex: str, git_remote_url: str, git_root: Path, silent: bool):
  run(cmd=['ls'], silent=silent)
  return


@__ensure_parameters
def pull(branch_regex: str, git_remote_url: str, git_root: Path, silent: bool):
  return
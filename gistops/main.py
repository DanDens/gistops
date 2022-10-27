#!/usr/bin/env python3
import os
import sys
import logging
from functools import partial
from pathlib import Path
from typing import Callable, List

import fire

# adjust PYTHON_PATH for debugging of lambda app
sys.path.append(str(Path(os.path.realpath(__file__)).parent))
from gistops.gists import assert_git_root, assert_git_attributes
from gistops.gists import Gist, GistError, iterate_gists
from gistops.shell import shrun
from gistops.mirror import mirror, as_remote, GitRemote
from gistops.render import render 
from gistops.publish import publish
from gistops.version import __version__


class GistOps(object):
    f"""{__version__} - Operations on Gists managed by Git"""


    def __init__(self, 
      cwd: str=str(Path.cwd()), 
      git_hash: str=None,
      quiet: bool=False,
      protected_envs: List[str]=os.environ.get(
        'GISTOPS_PROTECTED_ENVS',list()),
      dry_run: bool=False):

        logger = logging.getLogger()
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(os.environ.get('LOG_LEVEL','INFO'))

        ############
        # Git Root #
        ############
        # Remember parameters
        self.__git_diff_hash = git_hash
        # Make git root current working directory 
        # and make path relative to git root
        self.__git_root = assert_git_root(Path(cwd).resolve())
        os.chdir(str(self.__git_root))
        self.__gist_path = Path(cwd).relative_to(self.__git_root)

        ##################
        # Protected Envs #
        ##################
        # Remove sensitive keys from os.environ 
        # when running executables on the shell
        protected_envs.extend([
          'GISTOPS_GIT_SOURCE_URL',
          'GISTOPS_GIT_SOURCE_USERNAME',
          'GISTOPS_GIT_SOURCE_PASSWORD',
          'GISTOPS_GIT_TARGET_URL',
          'GISTOPS_GIT_TARGET_USERNAME',
          'GISTOPS_GIT_TARGET_PASSWORD'
        ])
        shell_env = os.environ.copy()
        for protected_key in protected_envs:
          if protected_key in shell_env: 
            del shell_env[protected_key]

        ###################
        # Configure Shell #
        ###################
        self.__shrun: Callable[[List[str]], str] = partial(
          shrun,
          env=shell_env,
          cwd=self.__git_root.resolve(),
          hide_streams=False,
          log_cmd_level=logging.INFO,
          enforce_absolute_silence=quiet,
          do_not_execute=False) 

        self.__dry_run = dry_run

        ##################
        # Git Attributes #
        ##################
        assert_git_attributes(shrun=self.__shrun, git_root=self.__git_root)

    def version(self) -> str:
        """Just print the version"""
        logger = logging.getLogger()
        logger.info(__version__)


    def validate(self):
        """Validate gists as defined in .gitattributes"""
        logger = logging.getLogger()
        
        shrun = partial(
          self.__shrun,
          enforce_absolute_silence=True)

        try:
          for gist in iterate_gists(
            shrun=shrun, 
            git_root=self.__git_root, 
            gist_path=self.__gist_path, 
            git_diff_hash=self.__git_diff_hash):
              render(shrun=shrun, gist=gist, dry_run=True)
              publish(shrun=shrun, gist=gist, dry_run=True)
              logger.info(f'{gist.path} valid') 
        except GistError as err:
            logger.error(f'{gist.path} invalid: {err}') 


    def render(self):
        """Render gists using pandoc configured by .gitattributes"""
        for gist in iterate_gists(
          shrun=self.__shrun, 
          git_root=self.__git_root, 
          gist_path=self.__gist_path, 
          git_diff_hash=self.__git_diff_hash):
            render(shrun=self.__shrun,gist=gist,dry_run=self.__dry_run)


    def publish(self):
        """Publish gists using callbacks as defined in .gitattributes"""
        for gist in iterate_gists(
          shrun=self.__shrun, 
          git_root=self.__git_root, 
          gist_path=self.__gist_path, 
          git_diff_hash=self.__git_diff_hash):
            publish(shrun=self.__shrun,gist=gist,dry_run=self.__dry_run)


    def mirror(self,
      branch_regex: str,
      git_src_url: str=None,
      git_trg_url: str=None,
      git_src_username: str=None,
      git_src_password: str=None,
      git_trg_username: str=None,
      git_trg_password: str=None ):
        """Push mirror branch(s) to remote"""

        if git_src_url is None: 
          git_src_url=os.environ['GISTOPS_GIT_SOURCE_URL']
        if git_trg_url is None: 
          git_trg_url=os.environ['GISTOPS_GIT_TARGET_URL']
        if git_src_username is None:
          git_src_username=os.environ.get('GISTOPS_GIT_SOURCE_USERNAME', None)
        if git_src_password is None:
          git_src_password=os.environ.get('GISTOPS_GIT_SOURCE_PASSWORD', None)
        if git_trg_username is None:
          git_trg_username=os.environ.get('GISTOPS_GIT_TARGET_USERNAME', None)
        if git_trg_password is None:
          git_trg_password=os.environ.get('GISTOPS_GIT_TARGET_PASSWORD', None)
      

        mirror(
          shrun = self.__shrun,
          git_remote_src = as_remote(
            self.__shrun, git_src_url, git_src_username, git_src_password ),
          git_remote_trg = as_remote(
            self.__shrun, git_trg_url, git_trg_username, git_trg_password ),
          branch_regex = branch_regex,
          dry_run = self.__dry_run)


if __name__ == '__main__':
    fire.Fire(GistOps)
